import hashlib
import urllib
import simplejson
from django.conf import settings
from django.utils.translation import ugettext as _
from httplib2 import Http
import logging

from .models import BaytPublishedCertificate

log = logging.getLogger(__name__)


def check_user_publish(user_id, course_id):
    if BaytPublishedCertificate.objects.filter(user_id=user_id, course_id=course_id).count() > 0:
        return True
    else:
        return False


class BaytApiError(Exception):
    pass


def post_to_bayt(email, course_name, secret_key=settings.BAYT_SECRET_KEY, api_base=settings.BAYT_API_BASE):
    """
    Makes an API post to Bayt.com to register the certificate.
    """

    url = api_base + "/api/edraak-api/post.adp?" + urllib.urlencode({
        'secret_key': secret_key,
        'valid_until': '06-2015',  # TODO: Make this dynamic
        'certificate_name': course_name.encode('UTF-8'),
        'email_address': email
    })

    resp, content = Http().request(url)
    json_content = simplejson.loads(content)

    if json_content['status'] == "NOT EXISTS":
        # Translators: Edraak-specific
        message = _("There's no user in Bayt the with the following email ({email})").format(email=email)
        log.warn(message)
        raise BaytApiError(message)

    log.info(u"Published a certificate to Bayt for {email}".format(email=email))
