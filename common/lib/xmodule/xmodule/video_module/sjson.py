"""
Functions specific to SRT transcript format.

MIME_TYPE = 'application/json'
"""
import json
from pysrt import SubRipItem, SubRipTime
from HTMLParser import HTMLParser

from . import TranscriptConvertEx


__all__ = ['convert_to_srt', 'convert_to_txt']


def _prepare_content(content):
    return json.loads(content)


def convert_to_srt(content, translate=lambda x: x):
    """
    Convert SJSON transcrit to SRT SubRip transcript.

    Args:
        content: dict, sjson subs.

    Raises:
        TranscriptConvertEx if SJSON transcript is broken.

    Returns:
        output, unicode.
    """
    content = _prepare_content(content)

    output = ''

    equal_len = len(content['start']) == len(content['end']) == len(content['text'])
    if not equal_len:
        raise TranscriptConvertEx(translate("Sjson transcript format is empty or incorrectly formed."))

    for i in range(len(content['start'])):
        item = SubRipItem(
            index=i,
            start=SubRipTime(milliseconds=content['start'][i]),
            end=SubRipTime(milliseconds=content['end'][i]),
            text=content['text'][i]
        )
        output += (unicode(item))
        output += '\n'
    return output


def convert_to_txt(content):
    """
    Convert SJSON transcript to TXT transcript.

    Args:
        content: list, "sjson" subs.

    Returns:
        output, str.
    """
    content = _prepare_content(content)
    text = content['text']
    return HTMLParser().unescape("\n".join(text))
