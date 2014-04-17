"""
Functions specific to SRT transcript format.
"""
import json
from pysrt import SubRipFile
from HTMLParser import HTMLParser

from .transcript import TranscriptFormat, Transcript


class Srt(TranscriptFormat):

    MIME_TYPE = 'application/x-subrip'


    @property
    def mime_type():
        return Srt.MIME_TYPE

    def convert_to(self, output_format, content):
        """
        Convert transcript from SRT SubRip to SJSON or TXT format.

        Output format is string representing convertion format: 'srt' or 'txt'
        """
        try:
            pysrt_obj = SubRipFile.from_string(content.decode('utf8'))
        except Exception as ex:
            msg = self._("SubRip transcripts file parsing error. Inner message is {error_message}").format(
                error_message=ex.message
            )
            raise Transcript.TranscriptConvertEx(msg)
        if not pysrt_obj:
            raise Transcript.TranscriptConvertEx(self._("Empty SubRip transcript after decoding."))

        if output_format.lower() == 'sjson':
            return self._convert_to_sjson(pysrt_obj)
        elif output_format.lower() == 'txt':
            return self._convert_to_txt(pysrt_obj)
        else:
            raise Transcript.TranscriptConvertEx(self._("Transcript convertion from {} to {} format is not supported").format(
                'SRT',
                output_format
            ))

    def _convert_to_sjson(self, pysrt_obj):
        """=
        Convert transcript from SRT SubRip to SJSON format.

        Args:
            `pysrt_obj` decoded srt transcript.

        Returns:
            subs: dict, if all subs are generated and saved successfully.
        """
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


    def _convert_to_txt(self, pysrt_obj):
        """
        Convert SRT transcrit to TXT transcript.

        Args:
            `pysrt_obj` decoded srt transcript.

        Returns:
            output, srt ? unicode.
        """
        return HTMLParser().unescape(pysrt_obj.text)
