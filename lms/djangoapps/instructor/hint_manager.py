"""
Views for hint management.

Along with the crowdsource_hinter xmodule, this code is still
experimental, and should not be used in new courses, yet.
"""

import json
import requests

from django.http import HttpResponse, Http404
from django_future.csrf import ensure_csrf_cookie
from django.conf import settings

from mitxmako.shortcuts import render_to_response, render_to_string

from courseware.courses import get_course_with_access

special_keys = ['field', 'op', 'location']


@ensure_csrf_cookie
def hint_manager(request, course_id):
    try:
        get_course_with_access(request.user, course_id, 'staff', depth=None)
    except Http404:
        out = 'Sorry, but students are not allowed to access the hint manager!'
        return HttpResponse(out)
    if request.method == 'GET':
        return pick_problem(request, course_id)
    field = request.POST['field']
    if not (field == 'mod_queue' or field == 'hints'):
        # Invalid field.  (Don't let users continue - they may overwrite other db's)
        out = 'Error in hint manager - an invalid field was accessed.'
        return HttpResponse(out)

    switch_dict = {
        'delete hints': delete_hints,
        'switch fields': lambda *args: None,    # Takes any number of arguments, returns None.
        'change votes': change_votes,
        'add hint': add_hint,
        'approve': approve,
    }

    # Do the operation requested, and collect any error messages.
    error_text = switch_dict[request.POST['op']](request, course_id, field)
    if error_text is None:
        error_text = ''
    render_dict = get_hints(request, course_id)
    render_dict.update({'error': error_text})
    rendered_html = render_to_string('instructor/hint_manager_inner.html', render_dict)
    return HttpResponse(json.dumps({'success': True, 'contents': rendered_html}))


def pick_problem(request, course_id):
    """Make a menu of all the problems that have hinting."""
    payload = {'in_dict_json': json.dumps({
        'course': course_id,
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/list_problems', params=payload)
    response_dict = json.loads(r.text)
    # r_d['problems'] contains a list of [location, name] tuples.
    return render_to_response(
        'instructor/hint_manager.html',
        {'problems': response_dict['problems']}
    )


def get_hints(request, course_id):
    """
    Load all of the hints submitted to the course.

    Args:
    `request` -- Django request object.  Required to have the following keys:
        - 'field' - either 'mod_queue' or 'hints'
        - 'location' - a json-encoded list representing the location of the problem.
    `course_id` -- The course id, like 'Me/19.002/test_course'

    Keys in returned dict:
        - 'field': Same as input
        - 'other_field': 'mod_queue' if `field` == 'hints'; and vice-versa.
        - 'field_label', 'other_field_label': English name for the above.
        - 'all_hints': A list of [answer, pk dict] pairs, representing all hints.
          Sorted by answer.
        - 'id_to_name': A dictionary mapping problem id to problem name.
    """
    field = request.POST['field']
    if field == 'mod_queue':
        other_field = 'hints'
        field_label = 'Hints Awaiting Moderation'
        other_field_label = 'Approved Hints'
    elif field == 'hints':
        other_field = 'mod_queue'
        field_label = 'Approved Hints'
        other_field_label = 'Hints Awaiting Moderation'

    # Make request to edInsights
    location_list = json.loads(request.POST['location'])
    payload = {'in_dict_json': json.dumps({
        'location': location_list,
        'field': field,
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/dump_hints', params=payload)
    response_dict = json.loads(r.text)
    # all_hints is a list of [id, answer, hint text, votes] sublists for each hint.
    all_hints = response_dict['hints']
    # Sort by answer, then by number of votes.
    all_hints.sort(key=lambda sublist: sublist[3], reverse=True)    # Number of votes
    all_hints.sort(key=lambda sublist: sublist[1])    # Answer
    render_dict = {'field': field,
                   'other_field': other_field,
                   'field_label': field_label,
                   'other_field_label': other_field_label,
                   'all_hints': all_hints,
                   'location': request.POST['location'],
                   'problem_name': response_dict['problem_name']}
    return render_dict


def delete_hints(request, course_id, field):
    """
    Deletes the hints specified.

    `request.POST` contains some fields keyed by integers.  Each such field contains a
    [answer, pk] tuple.  These tuples specify the hints to be deleted.

    Example `request.POST`:
    {'op': 'delete_hints',
     'field': 'mod_queue',
     'location': [...],
      1: ['42.0', '3'],
      2: ['32.5', '12']}
    """
    pks_to_delete = []
    for key in request.POST:
        if key in special_keys:
            continue
        answer, pk = request.POST.getlist(key)
        pks_to_delete.append(pk)
    payload = {'in_dict_json': json.dumps({
        'to_delete': pks_to_delete
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/delete_hints', params=payload)
    response = json.loads(r.text)
    if not response['success']:
        return response['error']


def change_votes(request, course_id, field):
    """
    Updates the number of votes.

    The numbered fields of `request.POST` contain [problem_id, answer, pk, new_votes] tuples.
    - Very similar to `delete_hints`.
    """
    updated_votes = []    # List of [pk, new_votes]
    for key in request.POST:
        if key in special_keys:
            continue
        updated_votes.append(request.POST.getlist(key)[1:3])
    payload = {'in_dict_json': json.dumps({
        'updated_votes': updated_votes
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/change_votes', params=payload)
    response = json.loads(r.text)
    if not response['success']:
        return response['error']


def add_hint(request, course_id, field):
    """
    Add a new hint.  `request.POST`:
    op
    field
    location - A json-encoded location tuple for the problem
    answer - The answer to which a hint will be added
    hint - The text of the hint
    """
    location = request.POST['location']
    answer = request.POST['answer']
    hint_text = request.POST['hint']
    payload = {'in_dict_json': json.dumps({
        'location': json.loads(location),
        'answer': answer,
        'hint': hint_text,
        'user': 'instructor',
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/submit_hint', params=payload)
    response = json.loads(r.text)
    if not response['success']:
        return response['error']


def approve(request, course_id, field):
    """
    Approve a list of hints, moving them from the mod_queue to the real
    hint list.  POST:
    op, field
    (some number) -> [problem, answer, pk]
    """
    to_approve = []    # List of pk's to approve.
    for key in request.POST:
        if key in special_keys:
            continue
        answer, pk = request.POST.getlist(key)
        to_approve.append(pk)
    payload = {'in_dict_json': json.dumps({
        'to_approve': to_approve
    })}
    r = requests.get(settings.EDINSIGHTS_SERVER_URL + 'query/approve_hints', params=payload)
    response = json.loads(r.text)
    if not response['success']:
        return response['error']
