
import json
import logging
from django.contrib.auth.models import User
from courseware.models import StudentModule
from courseware.model_data import ModelDataCache
from courseware.module_render import get_module

from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
import track.views

from celery import task, current_task
from celery.utils.log import get_task_logger
from time import sleep

logger = get_task_logger(__name__)

# celery = Celery('tasks', broker='django://')

log = logging.getLogger(__name__)



@task
def add(x, y):
    return x + y


@task
def echo(value):
    if value == 'ping':
        result = 'pong'
    else:
        result = 'got: {0}'.format(value)

    return result


@task
def waitawhile(value):
    for i in range(value):
        sleep(1)  # in seconds
        logger.info('Waited {0} seconds...'.format(i))
        current_task.update_state(state='PROGRESS',
                                  meta={'current': i, 'total': value})

    result = 'Yeah!'
    return result


class UpdateProblemModuleStateError(Exception):
    pass


def _update_problem_module_state(request, course_id, problem_url, student, update_fcn, action_name, filter_fcn):
    '''
    Performs generic update by visiting StudentModule instances with the update_fcn provided

    If student is None, performs update on modules for all students on the specified problem
    '''
    module_state_key = problem_url

    # find the problem descriptor, if any:
    try:
        module_descriptor = modulestore().get_instance(course_id, module_state_key)
    except ItemNotFoundError:
        return "<font color='red'>Couldn't find problem with that urlname.  </font>"
    if module_descriptor is None:
        return "<font color='red'>Couldn't find problem with that urlname.  </font>"

    # find the module in question
    modules_to_update = StudentModule.objects.filter(course_id=course_id,
                                                     module_state_key=module_state_key)

    # give the option of regrading an individual student. If not specified,
    # then regrades all students who have responded to a problem so far
    if student is not None:
        modules_to_update = modules_to_update.filter(student_id=student.id)

    if filter_fcn is not None:
        modules_to_update = filter_fcn(modules_to_update)

    num_updated = 0
    num_attempted = 0
    for module_to_update in modules_to_update:
        num_attempted += 1
        try:
            if update_fcn(request, module_to_update, module_descriptor):
                num_updated += 1
        except UpdateProblemModuleStateError as e:
            # something bad happened, so exit right away
            msg = "<font color='red'>{0}</font>".format(e.message)
            return msg

    # done with looping through all modules, so just return final statistics:
    if student is not None:
        if num_attempted == 0:
            msg = "<font color='red'>Unable to find submission to be {action} for student '{student}' and problem '{problem}'.  </font>"
        elif num_updated == 0:
            msg = "<font color='red'>Problem failed to be {action} for student '{student}' and problem '{problem}'!</font>"
        else:
            msg = "<font color='green'>Problem successfully {action} for student '{student}' and problem '{problem}'</font>"
    elif num_attempted == 0:
        msg = "<font color='red'>Unable to find any students with submissions to be {action} for problem '{problem}'.  </font>"
    elif num_updated == 0:
        msg = "<font color='red'>Problem failed to be {action} for any of {attempted} students for problem '{problem}'!</font>"
    elif num_updated == num_attempted:
        msg = "<font color='green'>Problem successfully {action} for {attempted} students for problem '{problem}'!</font>"
    elif num_updated < num_attempted:
        msg = "<font color='red'>Problem {action} for {updated} of {attempted} students for problem '{problem}'!</font>"

    msg = msg.format(action=action_name, updated=num_updated, attempted=num_attempted, student=student, problem=module_state_key)
    return msg


def _update_problem_module_state_for_student(request, course_id, problem_url, student_identifier,
                                             update_fcn, action_name, filter_fcn=None):
    msg = ''
    # try to uniquely id student by email address or username
    try:
        if "@" in student_identifier:
            student_to_update = User.objects.get(email=student_identifier)
        elif student_identifier is not None:
            student_to_update = User.objects.get(username=student_identifier)
        msg = "Found a single student to be {action}.  ".format(action=action_name)
        msg += _update_problem_module_state(request, course_id, problem_url, student_to_update, update_fcn, action_name, filter_fcn)
    except:
        msg = "<font color='red'>Couldn't find student with that email or username.  </font>"

    return msg


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
        log.debug(msg)
        raise UpdateProblemModuleStateError(msg)

    if not hasattr(instance, 'regrade_problem'):
        # if the first instance doesn't have a regrade method, we should
        # probably assume that no other instances will either.
        msg = "Specified problem does not support regrading."
        raise UpdateProblemModuleStateError(msg)

    result = instance.regrade_problem()
    if 'success' not in result:
        # don't consider these fatal, but false means that the individual call didn't complete:
        log.debug("error processing regrade call for problem {loc} and student {student}: "
                 "unexpected response {msg}".format(msg=result, loc=module_state_key, student=student))
        return False
    elif result['success'] != 'correct' and result['success'] != 'incorrect':
        log.debug("error processing regrade call for problem {loc} and student {student}: "
                  "{msg}".format(msg=result['success'], loc=module_state_key, student=student))
        return False
    else:
        track.views.server_track(request,
                                 '{instructor} regrade problem {problem} for student {student} '
                                 'in {course}'.format(student=student.id,
                                                      problem=module_to_regrade.module_state_key,
                                                      instructor=request.user,
                                                      course=course_id),
                                 {},
                                 page='idashboard')
        return True


def filter_problem_module_state_for_done(modules_to_update):
    return modules_to_update.filter(state__contains='"done": true')


def _regrade_problem_for_student(request, course_id, problem_url, student_identifier):
    action_name = 'regraded'
    update_fcn = _regrade_problem_module_state
    filter_fcn = filter_problem_module_state_for_done
    return _update_problem_module_state_for_student(request, course_id, problem_url, student_identifier,
                                                    update_fcn, action_name, filter_fcn)


def _regrade_problem_for_all_students(request, course_id, problem_url):
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
