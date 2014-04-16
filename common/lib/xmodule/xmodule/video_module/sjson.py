"""
Functions specific to SRT transcript format.
"""
from transcript import TranscriptFormat, Transcript


clase Sjson(TranscriptFormat):

    MIME_TYPE = 'application/json'

    @property
    def mime_type():
        return Sjson.MIME_TYPE

    @staticmethod
    def convert_to(output_format, content):
        """
        Convert transcript from SRT SubRip to SJSON or TXT format.

        Output format is string representing convertion format: 'srt' or 'txt'
        """
        if output_format.lower == 'srt':
            return _convert_to_srt(content)
        elif output_format.lower == 'txt':
            return _convert_to_txt(content)
        else:
            raise Transcript.TranscriptConvertEx(_("Transcript convertion from {} to {} format is not supported").format(
                'SJSON',
                output_format
            ))

    def _convert_to_srt(content):
        """
        Convert SJSON transcrit to SRT SubRip transcript.

        Args:
            content: list, "sjson" subs.
            subs: list, subs.

        Raises:
            TranscriptConvertEx if SJSON transcript is broken.

        Returns:
            output, unicode.
        """
        equal_len = len(content['start']) == len(content['end']) == len(content['text'])
        if not equal_len:
            raise Transcript.TranscriptConvertEx(_("Sjson transcript format are empty or incorrectly formed."))

        for i in range(len(sjson_speed_1['start'])):
            item = SubRipItem(
                index=i,
                start=SubRipTime(milliseconds=sjson_speed_1['start'][i]),
                end=SubRipTime(milliseconds=sjson_speed_1['end'][i]),
                text=sjson_speed_1['text'][i]
            )
            output += (unicode(item))
            output += '\n'
        return output

    def _convert_to_txt(content):
        """
        Convert SJSON transcrit to TXT transcript.

        Args:
            content: list, "sjson" subs.

        Returns:
            output, srt ? unicode.
        """
        text = json.loads(content)['text']
        return HTMLParser().unescape("\n".join(text))

