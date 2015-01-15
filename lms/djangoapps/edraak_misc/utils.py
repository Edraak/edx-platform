from courseware.access import has_access
from django.conf import settings


def is_certificate_allowed(user, course):
    if not settings.FEATURES.get('ENABLE_ISSUE_CERTIFICATE'):
        return False

    return course.has_ended() or has_access(user, 'staff', course.id)


def sort_closed_courses_to_bottom(courses):
    """
    Sorts the courses by their `has_ended()`, open courses come first.
    """

    open_courses = [course for course in courses if not course.has_ended()]
    ended_courses = [course for course in courses if course.has_ended()]

    return open_courses + ended_courses