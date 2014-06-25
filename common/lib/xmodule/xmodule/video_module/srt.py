"""
Functions specific to SRT transcript format.
"""
import json
from pysrt import SubRipFile
from HTMLParser import HTMLParser

from .transcript import TranscriptFormat, TranscriptConvertEx


class Srt(object):
    """
    Container 'srt' methods.
    """

    MIME_TYPE =     'application/x-subrip'

    @property
    def mime_type():
        return Srt.MIME_TYPE

    def set_content(content):
        """
        Add content for future work
        """
        self._content = content
        return self

    def _prepare_content(self):
        """
        Convert content to PySrt object.
        """
        try:
            pysrt_obj = SubRipFile.from_string(self._content.decode('utf8'))
        except Exception as ex:
            msg = self._("SubRip transcripts file parsing error. Inner message is {error_message}").format(
                error_message=ex.message
            )
            raise TranscriptConvertEx(msg)
        if not pysrt_obj:
            raise TranscriptConvertEx(self._("Empty SubRip transcript after decoding."))

        return pysrt_obj

    def _convert_to_sjson(self, pysrt_obj):
        """
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
            output, srt.
        """
        return HTMLParser().unescape(pysrt_obj.text)
