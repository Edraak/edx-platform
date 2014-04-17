"""
Functions specific to SRT transcript format.
"""
from pysrt import SubRipFile

from .transcript import TranscriptFormat, Transcript


class Srt(TranscriptFormat):

    MIME_TYPE = 'application/x-subrip'


    @property
    def mime_type():
        return Srt.MIME_TYPE

    @staticmethod
    def convert_to(output_format, content):
        """
        Convert transcript from SRT SubRip to SJSON or TXT format.

        Output format is string representing convertion format: 'srt' or 'txt'
        """
        if output_format.lower == 'sjson':
            return _convert_to_sjon(content)
        elif output_format.lower == 'txt':
            return _convert_to_txt(content)
        else:
            raise Transcript.TranscriptConvertEx(self._("Transcript convertion from {} to {} format is not supported").format(
                'SRT',
                output_format
            ))

    @staticmethod
    def _convert_to_sjson(content):
        """=
        Convert transcript from SRT SubRip to SJSON format.

        Args:
            speed_subs: dictionary {speed: sub_id, ...}
            content:unicode, content of source subs.
            language: str, language of translation of transcripts

        Returns:
            subs: list, if all subs are generated and saved successfully.

        Raises:
            TranscriptConvertEx when convertion fails
        """

        try:
            srt_subs_obj = SubRipFile.from_string(content)
        except Exception as ex:
            msg = self._("Something wrong with SubRip transcripts file during parsing. Inner message is {error_message}").format(
                error_message=ex.message
            )
            raise TranscriptConvertEx(msg)
        if not srt_subs_obj:
            raise TranscriptConvertEx(self._("Something wrong with SubRip transcripts file during parsing."))

        sub_starts = []
        sub_ends = []
        sub_texts = []

        for sub in srt_subs_obj:
            sub_starts.append(sub.start.ordinal)
            sub_ends.append(sub.end.ordinal)
            sub_texts.append(sub.text.replace('\n', ' '))

        subs = {
            'start': sub_starts,
            'end': sub_ends,
            'text': sub_texts}

        return subs

    def _convert_to_txt(content):
        """
        Convert SRT transcrit to TXT transcript.

        Args:
            content: dict, "sjson" subs.
            subs: list, subs.

        Raises:
           TranscriptConvertEx when convertion fails

        Returns:
            output, srt ? unicode.
        """

        text = SubRipFile.from_string(content.decode('utf8')).text

        try:
            text = SubRipFile.from_string(content.decode('utf8')).text
        except Exception as ex:
            msg = self._("Something wrong with SubRip transcripts file during parsing. Inner message is {error_message}").format(
                error_message=ex.message
            )
            raise TranscriptConvertEx(msg)
        return HTMLParser().unescape(text)
