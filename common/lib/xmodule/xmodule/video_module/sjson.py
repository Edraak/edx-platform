"""
Functions specific to SRT transcript format.
"""
import json
from pysrt import SubRipItem, SubRipTime
from HTMLParser import HTMLParser

from .transcript import TranscriptFormat, TranscriptConvertEx


class Sjson(TranscriptFormat):

    MIME_TYPE = 'application/json'

    @property
    def mime_type():
        return Sjson.MIME_TYPE

    def set_content(content):
        """
        Add content for future work
        """
        self._content = content
        return self

    def _prepare_content(content):
        return json.loads(content)

    def _convert_to_srt(self, content):
        """
        Convert SJSON transcrit to SRT SubRip transcript.

        Args:
            content: dict, sjson subs.

        Raises:
            TranscriptConvertEx if SJSON transcript is broken.

        Returns:
            output, unicode.
        """
        output = ''

        equal_len = len(content['start']) == len(content['end']) == len(content['text'])
        if not equal_len:
            raise TranscriptConvertEx(self._("Sjson transcript format is empty or incorrectly formed."))

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

    def _convert_to_txt(self, content):
        """
        Convert SJSON transcript to TXT transcript.

        Args:
            content: list, "sjson" subs.

        Returns:
            output, str.
        """
        text = content['text']
        return HTMLParser().unescape("\n".join(text))
