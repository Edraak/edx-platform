from django.utils.translation import ugettext as _
import hmac
from hashlib import sha256
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib import urlencode

ordered_hmac_keys = (
    'course_id',
    'email',
    'username',
    'name',
    'enrollment_action',
    'country',
    'level_of_education',
    'gender',
    'year_of_birth',
    'lang',
    'time',
)


class HttpResponseBadForusRequest(HttpResponseRedirect):
    def __init__(self, message):
        url = u'{base_url}?{params}'.format(
            base_url=settings.FORUS_ERROR_REDIRECT_URL,
            params=urlencode({
                'message': message.encode('utf-8')
            })
        )

        super(HttpResponseRedirect, self).__init__(url)


class ForusHmacError(Exception):
    pass


def validate_forus_params(params):
    forus_hmac = params.get('forus_hmac')

    if not forus_hmac:
        raise ForusHmacError(_('HMAC is missing'))

    params_pairs = [u'{0}={1}'.format(key, params[key]) for key in ordered_hmac_keys]
    msg_to_hash = u';'.join(params_pairs).encode('utf-8')

    secret_key = settings.FORUS_SECRET_KEY.encode('utf-8')

    dig = hmac.new(secret_key, msg_to_hash, digestmod=sha256)

    edraak_hmac = dig.hexdigest()

    if edraak_hmac != forus_hmac:
        raise ForusHmacError(_('HMAC is incorrect'))
