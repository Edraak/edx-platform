from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from util.json_request import JsonResponse
from courseware.courses import (
    get_courses,
    sort_by_announcement,
    course_image_url,
    get_course_about_section,
)

from edraak_misc.utils import edraak_courses_logic, get_absolute_url_prefix


def _get_course_status(course):
    if course.has_ended():
        return 'finished'
    elif course.enrollment_has_ended():
        return 'finishing'
    elif course.has_started():
        return 'open'
    elif course.enrollment_has_started():
        return 'upcoming'
    else:
        return 'hidden'


def courses(request):
    """
    Renders the courses list for the API.
    """

    # Hardcoded `AnonymousUser()` to hide unpublished courses always
    courses = get_courses(AnonymousUser())
    courses = sort_by_announcement(courses)
    courses = edraak_courses_logic(courses)


    courses_json = []

    prefix = get_absolute_url_prefix(request)

    for course in courses:
        courses_json.append({
            "id": unicode(course.id),
            "number": course.display_number_with_default,
            "name": course.display_name_with_default,
            "organization": course.display_org_with_default,
            "description": get_course_about_section(course, "short_description"),
            "startDate": course.start,
            "endDate": course.end,
            "enrollmentStartDate": course.enrollment_start,
            "enrollmentEndDate": course.enrollment_end,
            "overview": get_course_about_section(course, "overview"),
            "aboutPage": prefix + reverse('about_course', args=[unicode(course.id)]),
            "image": prefix + course_image_url(course),
            "state": _get_course_status(course),
        })

    return JsonResponse(courses_json)
