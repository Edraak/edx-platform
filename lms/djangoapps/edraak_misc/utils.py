from courseware.access import has_access
from django.conf import settings


def is_certificate_allowed(user, course):
    if not settings.FEATURES.get('ENABLE_ISSUE_CERTIFICATE'):
        return False

    return course.has_ended() or has_access(user, 'staff', course.id)
