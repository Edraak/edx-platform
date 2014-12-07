from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout, login
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User, AnonymousUser
from django.utils.translation import ugettext as _
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys import InvalidKeyError

from edxmako.shortcuts import render_to_response
from third_party_auth import pipeline
from microsite_configuration import microsite
from courseware.courses import get_course_with_access

from student.views import create_account as csrf_create_account
from student.helpers import auth_pipeline_urls
from student.models import AlreadyEnrolledError
from student.views import enroll, create_account as edx_create_account

from .models import ForusProfile
from .utils import validate_forus_params, ordered_hmac_keys, ForusHmacError, HttpResponseBadForusRequest

create_account = csrf_exempt(csrf_create_account)

import logging

log = logging.getLogger(__name__)


def auth(request):
    if request.user.is_authenticated():
        # Avoid complex and undefined use-cases with already logged in users
        logout(request)
        return HttpResponseRedirect(request.get_full_path())

    context = dict((key, request.GET[key]) for key in ordered_hmac_keys)
    course_string_id = request.GET.get("course_id")

    try:
        validate_forus_params(request.GET)
    except ForusHmacError as e:
        return HttpResponseBadForusRequest(e.message)

    try:
        course_key = SlashSeparatedCourseKey.from_deprecated_string(course_string_id)
    except InvalidKeyError:
        log.warning(
            u"User {username} tried to {action} with invalid course id: {course_id}".format(
                username=request.GET.get("username"),
                action=request.GET.get("enrollment_action"),
                course_id=course_string_id
            )
        )
        return HttpResponseBadForusRequest(_("Invalid course id"))

    try:
        user = User.objects.get(email=request.GET['email'])
        if not ForusProfile.is_forus_user(user):

            ForusProfile.create_for_user(user)

            if not user.is_active:
                user.activate = True
                user.save()

        # Simulate `django.contrib.auth.authenticate()` function
        user.backend = 'django.contrib.auth.backends.ModelBackend'

        login(request, user)

        try:
            enroll(user, course_key, check_access=True)
            return HttpResponseRedirect(reverse('course_root', args=[course_string_id]))
        except AlreadyEnrolledError:
            return HttpResponseRedirect(reverse('course_root', args=[course_string_id]))
        except Exception:
            return HttpResponseBadForusRequest(_("Could not enroll"))
    except User.DoesNotExist:
        course = get_course_with_access(AnonymousUser(), 'load', course_key)

        context.update({
            'password': pipeline.make_random_password(),
            "course": course,
            'forus_hmac': request.GET["forus_hmac"],
            'running_pipeline': None,
            'pipeline_urls': auth_pipeline_urls(pipeline.AUTH_ENTRY_REGISTER, course_id=request.GET['course_id']),
            'platform_name': microsite.get_value(
                'platform_name',
                settings.PLATFORM_NAME
            ),
            'selected_provider': '',
        })

        return render_to_response('edraak_forus/auth.html', context)


def create_account(request):
    validate_forus_params(request.POST)
    return edx_create_account(request)
