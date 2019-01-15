from django.middleware.csrf import get_token
from django.utils import six
from django.utils.encoding import smart_text
from django.utils.functional import lazy


def csrf(request):
    """
    Context processor that provides a CSRF token, or the string 'NOTPROVIDED' if
    it has not been provided by either a view decorator or the middleware
    """
    def _get_val():
        token = get_token(request)
        if token is None:
            # In order to be able to provide debugging info in the
            # case of misconfiguration, we use a sentinel value
            # instead of returning an empty dict.
            return 'NOTPROVIDED'
        else:
            return smart_text(token)
    _get_val = lazy(_get_val, six.text_type)

    return {'csrf_token': _get_val()}
