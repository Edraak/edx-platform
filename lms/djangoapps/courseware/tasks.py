
import json
#import logging
from time import sleep
from django.contrib.auth.models import User
from django.test.client import RequestFactory

from celery import task, current_task
from celery.signals import worker_ready
from celery.utils.log import get_task_logger

import mitxmako.middleware as middleware

from courseware.models import StudentModule, CourseTaskLog
from courseware.model_data import ModelDataCache
from courseware.module_render import get_module

from xmodule.modulestore.django import modulestore
import track.views


# define different loggers for use within tasks and on client side
task_log = get_task_logger(__name__)


@task
def waitawhile(value):
    for i in range(value):
        sleep(1)  # in seconds
        task_log.info('Waited {0} seconds...'.format(i))
        current_task.update_state(state='PROGRESS',
                                  meta={'current': i, 'total': value})

    result = 'Yeah!'
    return result


class UpdateProblemModuleStateError(Exception):
    pass


def _update_problem_module_state(request, course_id, module_state_key, student, update_fcn, action_name, filter_fcn):
    '''
    Performs generic update by visiting StudentModule instances with the update_fcn provided

    If student is None, performs update on modules for all students on the specified problem
    '''
    # add hack so that mako templates will work on celery worker server:
    # The initialization of Make templating is usually done when Django is
    # initializing middleware packages as part of processing a server request.
    # When this is run on a celery worker server, no such initialization is
    # called.  So we look for the result: the defining of the lookup paths
    # for templates.
    if 'main' not in middleware.lookup:
        task_log.info("Initializing Mako middleware explicitly")
        middleware.MakoMiddleware()

    # find the problem descriptor:
    module_descriptor = modulestore().get_instance(course_id, module_state_key)

    # find the module in question
    modules_to_update = StudentModule.objects.filter(course_id=course_id,
                                                     module_state_key=module_state_key)

    # give the option of regrading an individual student. If not specified,
    # then regrades all students who have responded to a problem so far
    if student is not None:
        modules_to_update = modules_to_update.filter(student_id=student.id)

    if filter_fcn is not None:
        modules_to_update = filter_fcn(modules_to_update)

    # perform the main loop
    num_updated = 0
    num_attempted = 0
    num_total = len(modules_to_update)  # TODO: make this more efficient.  Count()?

    def get_task_progress():
        progress = {'action_name': action_name,
                    'attempted': num_attempted,
                    'updated': num_updated,
                    'total': num_total,
                    }
        return progress

    task_log.info("Starting to process task {0}".format(current_task.request.id))

    for module_to_update in modules_to_update:
        num_attempted += 1
        # There is no try here:  if there's an error, we let it throw, and the task will
        # be marked as FAILED, with a stack trace.
        if update_fcn(request, module_to_update, module_descriptor):
            # If the update_fcn returns true, then it performed some kind of work.
            num_updated += 1

        # update task status:
        # TODO: decide on the frequency for updating this:
        #  -- it may not make sense to do so every time through the loop
        #  -- may depend on each iteration's duration
        current_task.update_state(state='PROGRESS', meta=get_task_progress())
        sleep(5)  # in seconds

    task_progress = get_task_progress()
    current_task.update_state(state='PROGRESS', meta=task_progress)

    task_log.info("Finished processing task")
    return task_progress


def _update_problem_module_state_for_student(request, course_id, problem_url, student_identifier,
                                             update_fcn, action_name, filter_fcn=None):
    msg = ''
    success = False
    # try to uniquely id student by email address or username
    try:
        if "@" in student_identifier:
            student_to_update = User.objects.get(email=student_identifier)
        elif student_identifier is not None:
            student_to_update = User.objects.get(username=student_identifier)
        return _update_problem_module_state(request, course_id, problem_url, student_to_update, update_fcn, action_name, filter_fcn)
    except User.DoesNotExist:
        msg = "Couldn't find student with that email or username."

    return (success, msg)


def _update_problem_module_state_for_all_students(request, course_id, problem_url, update_fcn, action_name, filter_fcn=None):
    return _update_problem_module_state(request, course_id, problem_url, None, update_fcn, action_name, filter_fcn)


def _regrade_problem_module_state(request, module_to_regrade, module_descriptor):
    '''
    Takes an XModule descriptor and a corresponding StudentModule object, and
    performs regrading on the student's problem submission.

    Throws exceptions if the regrading is fatal and should be aborted if in a loop.
    '''
    # unpack the StudentModule:
    course_id = module_to_regrade.course_id
    student = module_to_regrade.student
    module_state_key = module_to_regrade.module_state_key

    # reconstitute the problem's corresponding XModule:
    model_data_cache = ModelDataCache.cache_for_descriptor_descendents(course_id, student,
                                                                       module_descriptor)
    # Note that the request is passed to get_module() to provide xqueue-related URL information
    instance = get_module(student, request, module_state_key, model_data_cache,
                          course_id, grade_bucket_type='regrade')

    if instance is None:
        # Either permissions just changed, or someone is trying to be clever
        # and load something they shouldn't have access to.
        msg = "No module {loc} for student {student}--access denied?".format(loc=module_state_key,
                                                                             student=student)
        task_log.debug(msg)
        raise UpdateProblemModuleStateError(msg)

    if not hasattr(instance, 'regrade_problem'):
        # if the first instance doesn't have a regrade method, we should
        # probably assume that no other instances will either.
        msg = "Specified problem does not support regrading."
        raise UpdateProblemModuleStateError(msg)

    result = instance.regrade_problem()
    if 'success' not in result:
        # don't consider these fatal, but false means that the individual call didn't complete:
        task_log.debug("error processing regrade call for problem {loc} and student {student}: "
                 "unexpected response {msg}".format(msg=result, loc=module_state_key, student=student))
        return False
    elif result['success'] != 'correct' and result['success'] != 'incorrect':
        task_log.debug("error processing regrade call for problem {loc} and student {student}: "
                  "{msg}".format(msg=result['success'], loc=module_state_key, student=student))
        return False
    else:
        track.views.server_track(request,
                                 'regrade problem {problem} for student {student} '
                                 'in {course}'.format(student=student.id,
                                                      problem=module_to_regrade.module_state_key,
                                                      course=course_id),
                                 {},
                                 page='idashboard')
        return True


def filter_problem_module_state_for_done(modules_to_update):
    return modules_to_update.filter(state__contains='"done": true')


@task
def _regrade_problem_for_student(request, course_id, problem_url, student_identifier):
    action_name = 'regraded'
    update_fcn = _regrade_problem_module_state
    filter_fcn = filter_problem_module_state_for_done
    return _update_problem_module_state_for_student(request, course_id, problem_url, student_identifier,
                                                    update_fcn, action_name, filter_fcn)


def regrade_problem_for_student(request, course_id, problem_url, student_identifier):
    # First submit task.  Then  put stuff into table with the resulting task_id.
    result = _regrade_problem_for_student.apply_async(request, course_id, problem_url, student_identifier)
    task_id = result.id
    # TODO: for log, would want student_identifier to already be mapped to the student
    tasklog_args = {'course_id': course_id,
                    'task_name': 'regrade',
                    'task_args': problem_url,
                    'task_id': task_id,
                    'task_state': result.state,
                    'requester': request.user}

    CourseTaskLog.objects.create(**tasklog_args)
    return result


@task
def regrade_problem_for_all_students(request_environ, course_id, problem_url):
    factory = RequestFactory(**request_environ)
    request = factory.get('/')
    action_name = 'regraded'
    update_fcn = _regrade_problem_module_state
    filter_fcn = filter_problem_module_state_for_done
    return _update_problem_module_state_for_all_students(request, course_id, problem_url,
                                                         update_fcn, action_name, filter_fcn)


def _reset_problem_attempts_module_state(request, module_to_reset, module_descriptor):
    # modify the problem's state
    # load the state json and change state
    problem_state = json.loads(module_to_reset.state)
    if 'attempts' in problem_state:
        old_number_of_attempts = problem_state["attempts"]
        if old_number_of_attempts > 0:
            problem_state["attempts"] = 0
            # convert back to json and save
            module_to_reset.state = json.dumps(problem_state)
            module_to_reset.save()
            # write out tracking info
            track.views.server_track(request,
                                     '{instructor} reset attempts from {old_attempts} to 0 for {student} '
                                     'on problem {problem} in {course}'.format(old_attempts=old_number_of_attempts,
                                                                               student=module_to_reset.student,
                                                                               problem=module_to_reset.module_state_key,
                                                                               instructor=request.user,
                                                                               course=module_to_reset.course_id),
                                     {},
                                     page='idashboard')

    # consider the reset to be successful, even if no update was performed.  (It's just "optimized".)
    return True


def _reset_problem_attempts_for_student(request, course_id, problem_url, student_identifier):
    action_name = 'reset'
    update_fcn = _reset_problem_attempts_module_state
    return _update_problem_module_state_for_student(request, course_id, problem_url, student_identifier,
                                                    update_fcn, action_name)


def _reset_problem_attempts_for_all_students(request, course_id, problem_url):
    action_name = 'reset'
    update_fcn = _reset_problem_attempts_module_state
    return _update_problem_module_state_for_all_students(request, course_id, problem_url,
                                                         update_fcn, action_name)


def _delete_problem_module_state(request, module_to_delete, module_descriptor):
    '''
    delete the state
    '''
    module_to_delete.delete()
    return True


def _delete_problem_state_for_student(request, course_id, problem_url, student_ident):
    action_name = 'deleted'
    update_fcn = _delete_problem_module_state
    return _update_problem_module_state_for_student(request, course_id, problem_url,
                                                    update_fcn, action_name)


def _delete_problem_state_for_all_students(request, course_id, problem_url):
    action_name = 'deleted'
    update_fcn = _delete_problem_module_state
    return _update_problem_module_state_for_all_students(request, course_id, problem_url,
                                                         update_fcn, action_name)


@worker_ready.connect
def initialize_middleware(**kwargs):
    # The initialize Django middleware - some middleware components
    # are initialized lazily when the first request is served. Since
    # the celery workers do not serve request, the components never
    # get initialized, causing errors in some dependencies.
    # In particular, the Mako template middleware is used by some xmodules
    task_log.info("Initializing all middleware from worker_ready.connect hook")

    from django.core.handlers.base import BaseHandler
    BaseHandler().load_middleware()
