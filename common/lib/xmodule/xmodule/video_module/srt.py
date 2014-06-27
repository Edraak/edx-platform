"""
Functions specific to SRT transcript format.

MIME_TYPE = 'application/x-subrip'
"""
import json
from pysrt import SubRipFile
from HTMLParser import HTMLParser

from . import TranscriptConvertEx


__all__ = ['convert_to_txt', 'convert_to_sjson']


def _prepare_content(content, translate):
    """
    Convert content to PySrt object.

    Args:
        content, str, utf8 encoded string
    """

    try:
        pysrt_obj = SubRipFile.from_string(content.decode('utf8'))
    except Exception as ex:
        msg = translate("SubRip transcripts file parsing error. Inner message: {error_message}").format(
            error_message=unicode(ex)
        )
        raise TranscriptConvertEx(msg)
    if not pysrt_obj:
        raise TranscriptConvertEx(translate("Empty SubRip transcript after decoding."))

    return pysrt_obj

def convert_to_sjson(content, translate=lambda x: x):
    """
    Convert content to SRT SubRip then to SJSON format.

    Args:
        `content` str, srt transcript

    Returns:
        subs: dict, if all subs are generated and saved successfully.
    """
    pysrt_obj = _prepare_content(content, translate)

    sub_starts = []
    sub_ends = []
    sub_texts = []

    for sub in pysrt_obj:
        sub_starts.append(sub.start.ordinal)
        sub_ends.append(sub.end.ordinal)
        sub_texts.append(sub.text.replace('\n', ' '))

    subs =  {
        'start': sub_starts,
        'end': sub_ends,
        'text': sub_texts
    }

    return json.dumps(subs)


def convert_to_txt(content, translate=lambda x: x):
    """
    Convert content to SRT SubRip then to TXT format.

    Args:
        `content` str, srt transcript

    Returns:
        output, str.
    """
    pysrt_obj = _prepare_content(content, translate)
    return HTMLParser().unescape(pysrt_obj.text)
