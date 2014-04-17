"""
Functions specific to SRT transcript format.
"""
import json
from pysrt import SubRipItem, SubRipTime
from HTMLParser import HTMLParser

from .transcript import TranscriptFormat, Transcript


class Sjson(TranscriptFormat):

    MIME_TYPE = 'application/json'

    @property
    def mime_type():
        return Sjson.MIME_TYPE

    def convert_to(self, output_format, content):
        """
        Convert transcript from SJSON to SRT or TXT format.

        Output format is string representing convertion format: 'srt' or 'txt'
        """
        content = json.loads(content)

        if output_format.lower() == 'srt':
            return self._convert_to_srt(content)
        elif output_format.lower() == 'txt':
            return self._convert_to_txt(content)
        else:
            raise Transcript.TranscriptConvertEx(self._("Transcript convertion from {} to {} format is not supported").format(
                'SJSON',
                output_format
            ))

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
            raise Transcript.TranscriptConvertEx(self._("Sjson transcript format are empty or incorrectly formed."))

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
            output, srt ? unicode.
        """
        text = content['text']
        return HTMLParser().unescape("\n".join(text))

