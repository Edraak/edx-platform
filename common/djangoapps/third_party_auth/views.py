"""
Extra views required for SSO
"""
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseServerError, Http404, HttpResponseNotAllowed
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from social_django.views import complete
from social_django.utils import load_strategy, load_backend, psa
from social_core.utils import setting_name
from .models import SAMLConfiguration

URL_NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'


def inactive_user_view(request):
    """
    A newly or recently registered user has completed the social auth pipeline.
    Their account is not yet activated, but we let them login since the third party auth
    provider is trusted to vouch for them. See details in pipeline.py.

    The reason this view exists is that if we don't define this as the
    SOCIAL_AUTH_INACTIVE_USER_URL, inactive users will get sent to LOGIN_ERROR_URL, which we
    don't want.
    """
    # 'next' may be set to '/account/finish_auth/.../' if this user needs to be auto-enrolled
    # in a course. Otherwise, just redirect them to the dashboard, which displays a message
    # about activating their account.
    return redirect(request.GET.get('next', 'dashboard'))


def saml_metadata_view(request):
    """
    Get the Service Provider metadata for this edx-platform instance.
    You must send this XML to any Shibboleth Identity Provider that you wish to use.
    """
    if not SAMLConfiguration.is_enabled():
        raise Http404
    complete_url = reverse('social:complete', args=("tpa-saml", ))
    if settings.APPEND_SLASH and not complete_url.endswith('/'):
        complete_url = complete_url + '/'  # Required for consistency
    saml_backend = load_backend(load_strategy(request), "tpa-saml", redirect_uri=complete_url)
    metadata, errors = saml_backend.generate_metadata_xml()

    if not errors:
        return HttpResponse(content=metadata, content_type='text/xml')
    return HttpResponseServerError(content=', '.join(errors))


@csrf_exempt
@psa('{0}:complete'.format(URL_NAMESPACE))
def lti_login_and_complete_view(request, backend, *args, **kwargs):
    """This is a combination login/complete due to LTI being a one step login"""

    if request.method != 'POST':
        return HttpResponseNotAllowed('POST')

    request.backend.start()
    return complete(request, backend, *args, **kwargs)


def post_to_custom_auth_form(request):
    """
    Redirect to a custom login/register page.

    Since we can't do a redirect-to-POST, this view is used to pass SSO data from
    the third_party_auth pipeline to a custom login/register form (possibly on another server).
    """
    pipeline_data = request.session.pop('tpa_custom_auth_entry_data', None)
    if not pipeline_data:
        raise Http404
    # Verify the format of pipeline_data:
    data = {
        'post_url': pipeline_data['post_url'],
        # data: The provider info and user's name, email, etc. as base64 encoded JSON
        # It's base64 encoded because it's signed cryptographically and we don't want whitespace
        # or ordering issues affecting the hash/signature.
        'data': pipeline_data['data'],
        # The cryptographic hash of user_data:
        'hmac': pipeline_data['hmac'],
    }
    return render(request, 'third_party_auth/post_custom_auth_entry.html', data)
