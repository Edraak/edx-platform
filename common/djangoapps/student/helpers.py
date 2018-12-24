"""Helpers for the student app. """
import re
import time
import logging
from datetime import datetime
import urllib

from pytz import UTC

from embargo import api as embargo_api
from ipware.ip import get_ip

from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext as _, pgettext

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

import third_party_auth
from lms.djangoapps.verify_student.models import VerificationDeadline, SoftwareSecurePhotoVerification
from course_modes.models import CourseMode

from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore

# Note that this lives in openedx, so this dependency should be refactored.
from openedx.core.djangoapps.user_api.preferences import api as preferences_api


log = logging.getLogger("edx.student")

# Enumeration of per-course verification statuses
# we display on the student dashboard.
VERIFY_STATUS_NEED_TO_VERIFY = "verify_need_to_verify"
VERIFY_STATUS_SUBMITTED = "verify_submitted"
VERIFY_STATUS_APPROVED = "verify_approved"
VERIFY_STATUS_MISSED_DEADLINE = "verify_missed_deadline"
VERIFY_STATUS_NEED_TO_REVERIFY = "verify_need_to_reverify"

DISABLE_UNENROLL_CERT_STATES = [
    'generating',
    'ready',
]


class InvalidCourseIdError(Exception):
    pass


def check_verify_status_by_course(user, course_enrollments):
    """
    Determine the per-course verification statuses for a given user.

    The possible statuses are:
        * VERIFY_STATUS_NEED_TO_VERIFY: The student has not yet submitted photos for verification.
        * VERIFY_STATUS_SUBMITTED: The student has submitted photos for verification,
          but has have not yet been approved.
        * VERIFY_STATUS_APPROVED: The student has been successfully verified.
        * VERIFY_STATUS_MISSED_DEADLINE: The student did not submit photos within the course's deadline.
        * VERIFY_STATUS_NEED_TO_REVERIFY: The student has an active verification, but it is
            set to expire before the verification deadline for the course.

    It is is also possible that a course does NOT have a verification status if:
        * The user is not enrolled in a verified mode, meaning that the user didn't pay.
        * The course does not offer a verified mode.
        * The user submitted photos but an error occurred while verifying them.
        * The user submitted photos but the verification was denied.

    In the last two cases, we rely on messages in the sidebar rather than displaying
    messages for each course.

    Arguments:
        user (User): The currently logged-in user.
        course_enrollments (list[CourseEnrollment]): The courses the user is enrolled in.

    Returns:
        dict: Mapping of course keys verification status dictionaries.
            If no verification status is applicable to a course, it will not
            be included in the dictionary.
            The dictionaries have these keys:
                * status (str): One of the enumerated status codes.
                * days_until_deadline (int): Number of days until the verification deadline.
                * verification_good_until (str): Date string for the verification expiration date.

    """
    status_by_course = {}

    # Retrieve all verifications for the user, sorted in descending
    # order by submission datetime
    verifications = SoftwareSecurePhotoVerification.objects.filter(user=user)

    # Check whether the user has an active or pending verification attempt
    # To avoid another database hit, we re-use the queryset we have already retrieved.
    has_active_or_pending = SoftwareSecurePhotoVerification.user_has_valid_or_pending(
        user, queryset=verifications
    )

    # Retrieve verification deadlines for the enrolled courses
    enrolled_course_keys = [enrollment.course_id for enrollment in course_enrollments]
    course_deadlines = VerificationDeadline.deadlines_for_courses(enrolled_course_keys)

    recent_verification_datetime = None

    for enrollment in course_enrollments:

        # If the user hasn't enrolled as verified, then the course
        # won't display state related to its verification status.
        if enrollment.mode in CourseMode.VERIFIED_MODES:

            # Retrieve the verification deadline associated with the course.
            # This could be None if the course doesn't have a deadline.
            deadline = course_deadlines.get(enrollment.course_id)

            relevant_verification = SoftwareSecurePhotoVerification.verification_for_datetime(deadline, verifications)

            # Picking the max verification datetime on each iteration only with approved status
            if relevant_verification is not None and relevant_verification.status == "approved":
                recent_verification_datetime = max(
                    recent_verification_datetime if recent_verification_datetime is not None
                    else relevant_verification.expiration_datetime,
                    relevant_verification.expiration_datetime
                )

            # By default, don't show any status related to verification
            status = None

            # Check whether the user was approved or is awaiting approval
            if relevant_verification is not None:
                if relevant_verification.status == "approved":
                    status = VERIFY_STATUS_APPROVED
                elif relevant_verification.status == "submitted":
                    status = VERIFY_STATUS_SUBMITTED

            # If the user didn't submit at all, then tell them they need to verify
            # If the deadline has already passed, then tell them they missed it.
            # If they submitted but something went wrong (error or denied),
            # then don't show any messaging next to the course, since we already
            # show messages related to this on the left sidebar.
            submitted = (
                relevant_verification is not None and
                relevant_verification.status not in ["created", "ready"]
            )
            if status is None and not submitted:
                if deadline is None or deadline > datetime.now(UTC):
                    if has_active_or_pending:
                        # The user has an active verification, but the verification
                        # is set to expire before the deadline.  Tell the student
                        # to reverify.
                        status = VERIFY_STATUS_NEED_TO_REVERIFY
                    else:
                        status = VERIFY_STATUS_NEED_TO_VERIFY
                else:
                    # If a user currently has an active or pending verification,
                    # then they may have submitted an additional attempt after
                    # the verification deadline passed.  This can occur,
                    # for example, when the support team asks a student
                    # to reverify after the deadline so they can receive
                    # a verified certificate.
                    # In this case, we still want to show them as "verified"
                    # on the dashboard.
                    if has_active_or_pending:
                        status = VERIFY_STATUS_APPROVED

                    # Otherwise, the student missed the deadline, so show
                    # them as "honor" (the kind of certificate they will receive).
                    else:
                        status = VERIFY_STATUS_MISSED_DEADLINE

            # Set the status for the course only if we're displaying some kind of message
            # Otherwise, leave the course out of the dictionary.
            if status is not None:
                days_until_deadline = None

                now = datetime.now(UTC)
                if deadline is not None and deadline > now:
                    days_until_deadline = (deadline - now).days

                status_by_course[enrollment.course_id] = {
                    'status': status,
                    'days_until_deadline': days_until_deadline
                }

    if recent_verification_datetime:
        for key, value in status_by_course.iteritems():  # pylint: disable=unused-variable
            status_by_course[key]['verification_good_until'] = recent_verification_datetime.strftime("%m/%d/%Y")

    return status_by_course


def auth_pipeline_urls(auth_entry, redirect_url=None):
    """Retrieve URLs for each enabled third-party auth provider.

    These URLs are used on the "sign up" and "sign in" buttons
    on the login/registration forms to allow users to begin
    authentication with a third-party provider.

    Optionally, we can redirect the user to an arbitrary
    url after auth completes successfully.  We use this
    to redirect the user to a page that required login,
    or to send users to the payment flow when enrolling
    in a course.

    Args:
        auth_entry (string): Either `pipeline.AUTH_ENTRY_LOGIN` or `pipeline.AUTH_ENTRY_REGISTER`

    Keyword Args:
        redirect_url (unicode): If provided, send users to this URL
            after they successfully authenticate.

    Returns:
        dict mapping provider IDs to URLs

    """
    if not third_party_auth.is_enabled():
        return {}

    return {
        provider.provider_id: third_party_auth.pipeline.get_login_url(
            provider.provider_id, auth_entry, redirect_url=redirect_url
        ) for provider in third_party_auth.provider.Registry.accepting_logins()
    }


def _update_email_opt_in(request, org):
    """Helper function used to hit the profile API if email opt-in is enabled."""

    email_opt_in = request.POST.get('email_opt_in')
    if email_opt_in is not None:
        email_opt_in_boolean = email_opt_in == 'true'
        preferences_api.update_email_opt_in(request.user, org, email_opt_in_boolean)


def enroll(user, course_id, request, check_access):
    # Make sure the course exists
    # We don't do this check on unenroll, or a bad course id can't be unenrolled from
    if not modulestore().has_course(course_id):
        log.warning(
            u"User %s tried to enroll in non-existent course %s",
            user.username,
            course_id
        )
        raise InvalidCourseIdError()

    # Record the user's email opt-in preference
    if settings.FEATURES.get('ENABLE_MKTG_EMAIL_OPT_IN'):
        _update_email_opt_in(request, course_id.org)

    available_modes = CourseMode.modes_for_course_dict(course_id)

    # Check whether the user is blocked from enrolling in this course
    # This can occur if the user's IP is on a global blacklist
    # or if the user is enrolling in a country in which the course
    # is not available.
    redirect_url = embargo_api.redirect_if_blocked(
        course_id, user=user, ip_address=get_ip(request),
        url=request.path
    )
    if redirect_url:
        return redirect_url

    # Check that auto enrollment is allowed for this course
    # (= the course is NOT behind a paywall)
    if CourseMode.can_auto_enroll(course_id):
        # Enroll the user using the default mode (honor)
        # We're assuming that users of the course enrollment table
        # will NOT try to look up the course enrollment model
        # by its slug.  If they do, it's possible (based on the state of the database)
        # for no such model to exist, even though we've set the enrollment type
        # to "honor".

        # Exception is to be handled by the caller
        CourseEnrollment.enroll(user, course_id, check_access=check_access)

    # If we have more than one course mode or professional ed is enabled,
    # then send the user to the choose your track page.
    # (In the case of no-id-professional/professional ed, this will redirect to a page that
    # funnels users directly into the verification / payment flow)
    if CourseMode.has_verified_mode(available_modes) or CourseMode.has_professional_mode(available_modes):
        reverse("course_modes_choose", kwargs={'course_id': unicode(course_id)})

    # Otherwise, there is only one mode available (the default)
    # Success
    return None



# Query string parameters that can be passed to the "finish_auth" view to manage
# things like auto-enrollment.
POST_AUTH_PARAMS = ('course_id', 'enrollment_action', 'course_mode', 'email_opt_in', 'next_origin')


def get_next_url_for_login_page(request):
    """
    Determine the URL to redirect to following login/registration/third_party_auth

    The user is currently on a login or reigration page.
    If 'course_id' is set, or other POST_AUTH_PARAMS, we will need to send the user to the
    /account/finish_auth/ view following login, which will take care of auto-enrollment in
    the specified course.

    Otherwise, we go to the ?next= query param or to the dashboard if nothing else is
    specified.
    """
    redirect_to = request.GET.get('next', None)
    if not redirect_to:
        try:
            redirect_to = reverse('dashboard')
        except NoReverseMatch:
            redirect_to = reverse('home')
    if any(param in request.GET for param in POST_AUTH_PARAMS):
        # Before we redirect to next/dashboard, we need to handle auto-enrollment:
        params = [(param, request.GET[param]) for param in POST_AUTH_PARAMS if param in request.GET]
        params.append(('next', redirect_to))  # After auto-enrollment, user will be sent to payment page or to this URL
        redirect_to = '{}?{}'.format(reverse('finish_auth'), urllib.urlencode(params))
        # Note: if we are resuming a third party auth pipeline, then the next URL will already
        # be saved in the session as part of the pipeline state. That URL will take priority
        # over this one.
    return redirect_to


def is_origin_url_allowed(origin):
    """
    An Edraak change to determine if we can redirect the user to the
    requested origin or not. Allowed origins are identified in the
    configs files.
    :param origin: The requested origin
    :return: True if we can redirect, False otherwise
    """
    # Check if origin is a safe origin
    all_allowed = settings.AUTH_REDIRECT_ALLOW_ANY
    origin_allowed = origin in settings.AUTH_REDIRECT_ORIGINS_WHITELIST

    # Check if the origin matches any allowed pattern
    patterns = settings.AUTH_REDIRECT_REGX_ORIGINS
    evaluated_origins = filter(lambda x: re.match(x, origin), patterns)
    pattern_allowed = any(evaluated_origins)

    origin_recognized = all_allowed or origin_allowed or pattern_allowed
    is_enabled = settings.FEATURES.get("ENABLE_AUTH_EXTERNAL_REDIRECT")

    return is_enabled and origin_recognized


def is_hotmail_email(string):
    """
    Determine if an element in a list is a substring of string
    """
    outlook_domains = ['hotmail', 'outlook', 'live', 'outlook', 'msn']
    return any('{}.'.format(substring) in string for substring in outlook_domains)


def get_email_domain(email):
    """
    Determine the domain of an email
    """
    _user, domain = email.lower().rsplit('@', 1)
    if 'gmail.' in domain:
        domain = 'gmail'
    elif is_hotmail_email(domain):
        domain = 'hotmail'
    else:
        domain = 'other'
    return domain


def get_spam_name(email):
    """
    Determine name of spam folder
    """
    domain = get_email_domain(email)
    if domain is 'gmail':
        # Translators: Gmail Spam folder translation
        spam_name = pgettext('gmail', 'Spam')
    elif domain is 'hotmail':
        # Translators: Hotmail Junk folder translation
        spam_name = pgettext('hotmail', 'Junk')
    else:
        # Translators: Other email Spam folder translation
        spam_name = pgettext('other_email_providers', 'Spam')
    return spam_name
