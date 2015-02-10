"""
Module contains utils specific for video_module but not for transcripts.
"""
import json
import logging
import urllib
import requests
from django.conf import settings

from requests.exceptions import RequestException

log = logging.getLogger(__name__)


def create_youtube_string(module):
    """
    Create a string of Youtube IDs from `module`'s metadata
    attributes. Only writes a speed if an ID is present in the
    module.  Necessary for backwards compatibility with XML-based
    courses.
    """
    youtube_ids = [
        module.youtube_id_0_75,
        module.youtube_id_1_0,
        module.youtube_id_1_25,
        module.youtube_id_1_5
    ]
    youtube_speeds = ['0.75', '1.00', '1.25', '1.50']
    return ','.join([
        ':'.join(pair)
        for pair
        in zip(youtube_speeds, youtube_ids)
        if pair[1]
    ])


class NoHTML5SourcesForFreeAccess(Exception):
    """
    Free access is enabled but there's no proper HTML5 sources.
    """
    pass


def should_disable_youtube(html5_sources, youtube_streams):
    """
    Decide if the user is granted free-access and switch to HTML5 videos when possible.

    @author: Omar Al-Ithawi <oithawi@qrf.org>
    """
    if not settings.FEATURES.get('USE_FREE_ACCESS_VIDEOS', False):
        return False

    has_mp4 = False
    has_webm = False

    for source in html5_sources:
        if source.endswith('.mp4'):
            has_mp4 = True

        if source.endswith('.webm'):
            has_webm = True

    if has_mp4 and has_webm:
        return True
    else:
        msg = u'Missing video encoding: youtube=%(youtube)s has_mp4=%(has_mp4)s has_webm=%(has_webm)s'
        params = {
            "youtube": repr(youtube_streams),
            "has_mp4": has_mp4,
            "has_webm": has_webm,
        }

        log.error(msg, params)
        raise NoHTML5SourcesForFreeAccess(msg % params)


def get_video_from_cdn(cdn_base_url, original_video_url):
    """
    Get video URL from CDN.

    `original_video_url` is the existing video url.
    Currently `cdn_base_url` equals 'http://api.xuetangx.com/edx/video?s3_url='
    Example of CDN outcome:
        {
            "sources":
                [
                    "http://cm12.c110.play.bokecc.com/flvs/ca/QxcVl/u39EQbA0Ra-20.mp4",
                    "http://bm1.42.play.bokecc.com/flvs/ca/QxcVl/u39EQbA0Ra-20.mp4"
                ],
            "s3_url": "http://s3.amazonaws.com/BESTech/CS169/download/CS169_v13_w5l2s3.mp4"
        }
    where `s3_url` is requested original video url and `sources` is the list of
    alternative links.
    """

    if not cdn_base_url:
        return None

    request_url = cdn_base_url + urllib.quote(original_video_url)

    try:
        cdn_response = requests.get(request_url, timeout=0.5)
    except RequestException as err:
        log.info("Request timed out to CDN server: %s", request_url, exc_info=True)
        return None

    if cdn_response.status_code == 200:
        cdn_content = json.loads(cdn_response.content)
        return cdn_content['sources'][0]
    else:
        return None
