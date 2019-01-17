""" Helper methods for CourseModes. """
from urlparse import urljoin
from functools import reduce

from django.utils.translation import get_language, ugettext_lazy as _

from course_modes.models import CourseMode
from student.helpers import (
    VERIFY_STATUS_NEED_TO_VERIFY,
    VERIFY_STATUS_SUBMITTED,
    VERIFY_STATUS_APPROVED
)

from django.conf import settings
from django.core.urlresolvers import reverse

DISPLAY_VERIFIED = "verified"
DISPLAY_HONOR = "honor"
DISPLAY_AUDIT = "audit"
DISPLAY_PROFESSIONAL = "professional"

COURSE_INFO_PAGE = "COURSE_INFO"
SUCCESS_ENROLL_PAGE = "ENROLL_SUCCESS"


def get_progs_url(page):
    lang = ''

    if get_language() != 'ar':
        lang = 'en/'

    root = settings.PROGS_URLS['ROOT']

    url = reduce(urljoin, [root, lang, page])

    return url


def get_mktg_url(page):
    lang = ''

    if get_language() != 'ar':
        lang = 'en/'

    url = '{root}{lang}{page}'.format(
        root=settings.MKTG_URLS['ROOT'],
        lang=lang,
        page=page
    )
    
    return url


def get_mktg_for_course(page, course_id):
    """
    Redirects learner to the marketing site desired page

    :param page: desired page
    :param course_id: Course ID as string.
    :return (unicode) Redirect URL.
    """
    if settings.FEATURES.get('ENABLE_MKTG_SITE'):
        url = settings.MKTG_URLS.get(page)

        if url:
            return get_mktg_url(url.format(course_id=course_id))

    return reverse('dashboard')


def enrollment_mode_display(mode, verification_status, course_id):
    """ Select appropriate display strings and CSS classes.

        Uses mode and verification status to select appropriate display strings and CSS classes
        for certificate display.

        Args:
            mode (str): enrollment mode.
            verification_status (str) : verification status of student

        Returns:
            dictionary:
    """
    show_image = False
    image_alt = ''
    enrollment_title = ''
    enrollment_value = ''
    display_mode = _enrollment_mode_display(mode, verification_status, course_id)

    if display_mode == DISPLAY_VERIFIED:
        if verification_status in [VERIFY_STATUS_NEED_TO_VERIFY, VERIFY_STATUS_SUBMITTED]:
            enrollment_title = _("Your verification is pending")
            enrollment_value = _("Verified: Pending Verification")
            show_image = True
            image_alt = _("ID verification pending")
        elif verification_status == VERIFY_STATUS_APPROVED:
            enrollment_title = _("You're enrolled as a verified student")
            enrollment_value = _("Verified")
            show_image = True
            image_alt = _("ID Verified Ribbon/Badge")
    elif display_mode == DISPLAY_HONOR:
        enrollment_title = _("You're enrolled as an honor code student")
        enrollment_value = _("Honor Code")
    elif display_mode == DISPLAY_PROFESSIONAL:
        enrollment_title = _("You're enrolled as a professional education student")
        enrollment_value = _("Professional Ed")

    return {
        'enrollment_title': unicode(enrollment_title),
        'enrollment_value': unicode(enrollment_value),
        'show_image': show_image,
        'image_alt': unicode(image_alt),
        'display_mode': _enrollment_mode_display(mode, verification_status, course_id)
    }


def _enrollment_mode_display(enrollment_mode, verification_status, course_id):
    """Checking enrollment mode and status and returns the display mode
     Args:
        enrollment_mode (str): enrollment mode.
        verification_status (str) : verification status of student

    Returns:
        display_mode (str) : display mode for certs
    """
    course_mode_slugs = [mode.slug for mode in CourseMode.modes_for_course(course_id)]

    if enrollment_mode == CourseMode.VERIFIED:
        if verification_status in [VERIFY_STATUS_NEED_TO_VERIFY, VERIFY_STATUS_SUBMITTED, VERIFY_STATUS_APPROVED]:
            display_mode = DISPLAY_VERIFIED
        elif DISPLAY_HONOR in course_mode_slugs:
            display_mode = DISPLAY_HONOR
        else:
            display_mode = DISPLAY_AUDIT
    elif enrollment_mode in [CourseMode.PROFESSIONAL, CourseMode.NO_ID_PROFESSIONAL_MODE]:
        display_mode = DISPLAY_PROFESSIONAL
    else:
        display_mode = enrollment_mode

    return display_mode
