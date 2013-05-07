import json
import logging
from django.http import HttpResponse

from celery.result import AsyncResult
from celery.states import READY_STATES

from courseware.models import CourseTaskLog
from courseware.tasks import regrade_problem_for_all_students
from xmodule.modulestore.django import modulestore


# define different loggers for use within tasks and on client side
log = logging.getLogger(__name__)


def get_running_course_tasks(course_id):
    course_tasks = CourseTaskLog.objects.filter(course_id=course_id)
    for state in READY_STATES:
        course_tasks = course_tasks.exclude(task_state=state)
    return course_tasks


def _task_is_running(course_id, task_name, task_args, student=None):
    runningTasks = CourseTaskLog.objects.filter(course_id=course_id, task_name=task_name, task_args=task_args)
    if student is not None:
        runningTasks = runningTasks.filter(student=student)
    for state in READY_STATES:
        runningTasks = runningTasks.exclude(task_state=state)
    return len(runningTasks) > 0


def submit_regrade_problem_for_all_students(request, course_id, problem_url):
    # check arguments: in particular, make sure that problem_url is defined
    # (since that's currently typed in).  If the corresponding module descriptor doesn't exist,
    # an exception should be raised.  Let it continue to the caller.
    modulestore().get_instance(course_id, problem_url)

    # TODO: adjust transactions so that one request will not be about to create an
    # entry while a second is testing to see if the entry exists.  (Need to handle
    # quick accidental double-clicks when submitting.)

    # check to see if task is already running
    task_name = 'regrade'
    if _task_is_running(course_id, task_name, problem_url):
        # TODO: figure out how to return info that it's already running
        raise Exception("requested task is already running")

    # Create log entry now, so that future requests won't
    tasklog_args = {'course_id': course_id,
                    'task_name': task_name,
                    'task_args': problem_url,
                    'task_state': 'QUEUING',
                    'requester': request.user}
    course_task_log = CourseTaskLog.objects.create(**tasklog_args)

    # At a low level of processing, the task currently fetches some information from the web request.
    # This is used for setting up X-Queue, as well as for tracking.
    # An actual request will not successfully serialize with json or with pickle.
    # TODO: we can just pass all META info as a dict.
    request_environ = {'HTTP_USER_AGENT': request.META['HTTP_USER_AGENT'],
                       'REMOTE_ADDR': request.META['REMOTE_ADDR'],
                       'SERVER_NAME': request.META['SERVER_NAME'],
                       'REQUEST_METHOD': 'GET',
#                      'HTTP_X_FORWARDED_PROTO': request.META['HTTP_X_FORWARDED_PROTO'],
                      }

    # Submit task:
    task_args = [request_environ, course_id, problem_url]
    result = regrade_problem_for_all_students.apply_async(task_args)

    # Update info in table with the resulting task_id (and state).
    course_task_log.task_state = result.state
    course_task_log.task_id = result.id
    course_task_log.save()
    return course_task_log


def course_task_log_status(request, task_id=None):
    """
    This returns the status of a course-related task as a JSON-serialized dict.
    """
    output = {}
    if task_id is not None:
        output = _get_course_task_log_status(task_id)
    elif 'task_id' in request.POST:
        task_id = request.POST['task_id']
        output = _get_course_task_log_status(task_id)
    elif 'task_ids[]' in request.POST:
        tasks = request.POST.getlist('task_ids[]')
        for task_id in tasks:
            task_output = _get_course_task_log_status(task_id)
            if task_output is not None:
                output[task_id] = task_output
    # TODO decide whether to raise exception if bad args are passed.
    # May be enough just to return an empty output.

    return HttpResponse(json.dumps(output, indent=4))


def _get_course_task_log_status(task_id):
    """
    Get the status for a given task_id.

    Returns a dict, with the following keys:
      'task_id'
      'task_state'
      'in_progress': boolean indicating if the task is still running.
      'message': status message reporting on progress, or providing exception message if failed.
      'task_progress': dict containing progress information.  This includes:
          'attempted': number of attempts made
          'updated': number of attempts that "succeeded"
          'total': number of possible subtasks to attempt
          'action_name': user-visible verb to use in status messages.  Should be past-tense.
      'task_traceback': optional, returned if task failed and produced a traceback.
      'succeeded': on complete tasks, indicates if the task outcome was successful:
          did it achieve what it set out to do.
          This is in contrast with a successful task_state, which indicates that the
          task merely completed.

      If task doesn't exist, returns None.
    """
    # First check if the task_id is known
    try:
        course_task_log_entry = CourseTaskLog.objects.get(task_id=task_id)
    except CourseTaskLog.DoesNotExist:
        # TODO: log a message here
        return None

    # define ajax return value:
    output = {}

    # if the task is already known to be done, then there's no reason to query
    # the underlying task's result object:
    if course_task_log_entry.task_state not in READY_STATES:
        # we need to get information from the task result directly now.

        # Just create the result object, and pull values out once.
        # (If we check them later, the state and result may have changed.)
        result = AsyncResult(task_id)
        result_state = result.state
        returned_result = result.result
        result_traceback = result.traceback

        # Assume we don't always update the CourseTaskLog entry if we don't have to:
        entry_needs_saving = False

        if result_state == 'PROGRESS':
            # construct a status message directly from the task result's result:
            if hasattr(result, 'result') and 'attempted' in returned_result:
                fmt = "Attempted {attempted} of {total}, {action_name} {updated}"
                message = fmt.format(attempted=returned_result['attempted'],
                                     updated=returned_result['updated'],
                                     total=returned_result['total'],
                                     action_name=returned_result['action_name'])
                output['message'] = message
                log.info("task progress: {0}".format(message))
            else:
                log.info("still making progress... ")
            output['task_progress'] = returned_result

        elif result_state == 'SUCCESS':
            # on success, save out the result here, but the message
            # will be calculated later
            output['task_progress'] = returned_result
            course_task_log_entry.task_progress = json.dumps(returned_result)
            log.info("task succeeded: {0}".format(returned_result))
            entry_needs_saving = True

        elif result_state == 'FAILURE':
            # on failure, the result's result contains the exception that caused the failure
            exception = str(returned_result)
            course_task_log_entry.task_progress = exception
            entry_needs_saving = True
            output['message'] = exception
            log.info("task failed: {0}".format(returned_result))
            if result_traceback is not None:
                output['task_traceback'] = result_traceback

        # always update the entry if the state has changed:
        if result_state != course_task_log_entry.task_state:
            course_task_log_entry.task_state = result_state
            entry_needs_saving = True

        if entry_needs_saving:
            course_task_log_entry.save()
    else:
        # task is already known to have finished, but report on its status:
        if course_task_log_entry.task_progress is not None:
            output['task_progress'] = json.loads(course_task_log_entry.task_progress)

    # output basic information matching what's stored in CourseTaskLog:
    output['task_id'] = course_task_log_entry.task_id
    output['task_state'] = course_task_log_entry.task_state
    output['in_progress'] = course_task_log_entry.task_state not in READY_STATES

    if course_task_log_entry.task_state == 'SUCCESS':
        succeeded, message = _get_task_completion_message(course_task_log_entry)
        output['message'] = message
        output['succeeded'] = succeeded

    return output


def _get_task_completion_message(course_task_log_entry):
    """
    Construct progress message from progress information in CourseTaskLog entry.

    Returns (boolean, message string) duple.
    """
    succeeded = False

    if course_task_log_entry.task_progress is None:
        log.warning("No task_progress information found for course_task {0}".format(course_task_log_entry.task_id))
        return (succeeded, "No status information available")

    task_progress = json.loads(course_task_log_entry.task_progress)
    action_name = task_progress['action_name']
    num_attempted = task_progress['attempted']
    num_updated = task_progress['updated']
    # num_total = task_progress['total']
    if course_task_log_entry.student is not None:
        if num_attempted == 0:
            msg = "Unable to find submission to be {action} for student '{student}' and problem '{problem}'."
        elif num_updated == 0:
            msg = "Problem failed to be {action} for student '{student}' and problem '{problem}'!"
        else:
            succeeded = True
            msg = "Problem successfully {action} for student '{student}' and problem '{problem}'"
    elif num_attempted == 0:
        msg = "Unable to find any students with submissions to be {action} for problem '{problem}'."
    elif num_updated == 0:
        msg = "Problem failed to be {action} for any of {attempted} students for problem '{problem}'!"
    elif num_updated == num_attempted:
        succeeded = True
        msg = "Problem successfully {action} for {attempted} students for problem '{problem}'!"
    elif num_updated < num_attempted:
        msg = "Problem {action} for {updated} of {attempted} students for problem '{problem}'!"

    # Update status in task result object itself:
    message = msg.format(action=action_name, updated=num_updated, attempted=num_attempted,
                         student=course_task_log_entry.student, problem=course_task_log_entry.task_args)
    return (succeeded, message)
