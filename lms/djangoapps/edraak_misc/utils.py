import logging

from courseware.access import has_access
from django.conf import settings
from django.core.validators import validate_email as django_validate_email, ValidationError as DjangoValidationError
from validate_email import validate_email as strict_validate_email

log = logging.getLogger(__name__)

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


def validate_email(email):
    """
    Validate email, the strict or the quick way depending on `FEATURES['EMAIL_STRICT_VERIFICATION']`.
    """
    is_strict = settings.FEATURES.get('EMAIL_STRICT_VERIFICATION', True)
    log.info(u'Validating user email=%(email)s, strict_verification=%(is_strict)s', {
        'email': email,
        'is_strict': is_strict,
    })

    if is_strict:
        is_valid = strict_validate_email(
            email=email,
            check_mx=True,
            debug=True,
        )
    else:
        try:
            django_validate_email(email)
            is_valid = True
        except DjangoValidationError:
            is_valid = False

    log.info(u'Validating user email=%(email)s, strict_verification=%(is_strict)s, is_valid=%(is_valid)s', {
        'email': email,
        'is_strict': is_strict,
        'is_valid': is_valid,
    })

    return is_valid
