from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from util.json_request import JsonResponse
from openedx.core.lib.courses import course_image_url

from courseware.courses import (
    get_courses,
    sort_by_announcement,
    get_course_about_section,
)

from edraak_misc.utils import edraak_courses_logic, get_absolute_url_prefix


def _get_course_status(course):
    if course.has_ended():
        return 'finished'
    elif course.enrollment_has_ended():
        return 'finishing'
    elif course.is_self_paced():
        return 'self-paced'
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
        video_tag = get_course_about_section(course, "video")
        youtube_id = video_tag[video_tag.find("embed") + 6:video_tag.find("?")]

        courses_json.append({
            "id": unicode(course.id),
            "number": course.display_number_with_default,
            "name": course.display_name_with_default,
            "organization": course.display_org_with_default,
            "description": get_course_about_section(course, "short_description").strip(),
            "startDate": course.start,
            "endDate": course.end,
            "enrollmentStartDate": course.enrollment_start,
            "enrollmentEndDate": course.enrollment_end,
            "overview": get_course_about_section(course, "overview").strip(),
            "aboutPage": prefix + reverse('about_course', args=[unicode(course.id)]),
            "image": prefix + course_image_url(course),
            "state": _get_course_status(course),
            "youtube_id": youtube_id,
            "effort": get_course_about_section(course, "effort").strip(),
        })

    return JsonResponse(courses_json)
