from django.core.urlresolvers import reverse
from django.contrib.auth.models import AnonymousUser

from django.conf import settings

from util.json_request import JsonResponse
from openedx.core.lib.courses import course_image_url

from courseware.courses import (
    get_courses,
    get_course,
    sort_by_announcement,
    get_course_about_section,
)

import branding
import logging
from courseware.access import has_access

from edraak_misc.utils import edraak_courses_logic, get_absolute_url_prefix

log = logging.getLogger(__name__)

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


def courses(request, show_hidden):
    """
    Renders the courses list for the API.

    :param request: The django HttpRequest object.
    :param show_hidden: True or False, (controlled from the urls.py file) to show courses with
                        upcoming enrollment date.

    :return: JsonResponse with a list of the courses.
    """
    courses_list = branding.get_visible_courses()

    if not show_hidden:
        # Using `AnonymousUser()` to hide unpublished courses
        anonymous_user = AnonymousUser()

        # The logic bellow has been copied (with amendments) from `courseware.courses.get_courses`,
        # Just in case something changes with edX releases.
        permission_name = settings.COURSE_CATALOG_VISIBILITY_PERMISSION

        courses_list = [
            c for c in courses_list
            if has_access(anonymous_user, permission_name, c)
        ]

    courses_list = sort_by_announcement(courses_list)
    courses_list = edraak_courses_logic(courses_list)

    courses_json_list = []

    prefix = get_absolute_url_prefix(request)

    for course_overview in courses_list:

        try:
            course = get_course(course_overview.id)

            video_tag = get_course_about_section(request, course, "video")
            youtube_id = video_tag[video_tag.find("embed") + 6:video_tag.find("?")]

            courses_json_list.append({
                "id": unicode(course.id),
                "number": course.display_number_with_default,
                "name": course.display_name_with_default_escaped,
                "organization": course.display_org_with_default,
                "description": get_course_about_section(request, course, "short_description").strip(),
                "startDate": course.start,
                "endDate": course.end,
                "enrollmentStartDate": course.enrollment_start,
                "enrollmentEndDate": course.enrollment_end,
                "overview": get_course_about_section(request, course, "overview").strip(),
                "aboutPage": prefix + reverse('about_course', args=[unicode(course.id)]),
                "image": prefix + course_image_url(course),
                "state": _get_course_status(course),
                "youtube_id": youtube_id,
                "effort": get_course_about_section(request, course, "effort").strip(),
            })
        except ValueError:
            log.error(u"Course with id '{0}' not found".format(course_overview.id))


    return JsonResponse(courses_json_list)
