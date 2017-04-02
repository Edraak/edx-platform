from django import http
from django.conf import settings

from openedx.core.djangoapps.user_api.preferences.api import set_user_preference
from django.utils.translation import check_for_language
from django.views.decorators.csrf import csrf_exempt

from django.utils.translation import LANGUAGE_SESSION_KEY
from dark_lang import DARK_LANGUAGE_KEY


from helpers import get_any_safe_url


@csrf_exempt
def set_language(request):
    """
    A re-implementation of django_set_language that is suitable of Edraak's edX platform.

    It allows the user to redirect to the marketing site as well as the LMS.

    :param request: a request object for the view.
    :return HttpResponseRedirect: Redirects the user to the next safe URL.
    """

    default_redirect_hosts = (
        request.get_host(),
    )

    hosts = getattr(settings, 'SAFE_REDIRECT_HOSTS', default_redirect_hosts)

    safe_url = get_any_safe_url(
        hosts=hosts,
        urls=(
            request.REQUEST.get('next'),
            request.META.get('HTTP_REFERER'),
            '/',
        )
    )

    response = http.HttpResponseRedirect(safe_url)

    if request.method == 'POST':
        lang_code = request.POST.get('language', None)

        if lang_code and check_for_language(lang_code):

            if request.user.is_authenticated():
                set_user_preference(request.user, DARK_LANGUAGE_KEY, "ar")

            if hasattr(request, 'session'):
                request.session[LANGUAGE_SESSION_KEY] = lang_code
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    # Prevents accidental refresh: https://en.wikipedia.org/wiki/Post/Redirect/Get
    response.status_code = 303

    return response
