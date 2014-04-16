"""
Abstractions for trancripts.
"""
from srt import Srt
from sjson import Sjson


class TranscriptFormat(object):
    """
    Interface for transcript files.
    """
    @staticmethod
    def get_mime_type():
        raise NotImplemented

    @staticmethod
    def convert_to(output_format, content):
        raise NotImplemented


class Transcript(object):
    """
    Container for transcript methods.
    """
    mime_types = {
        'srt': 'application/x-subrip; charset=utf-8',
        'txt': 'text/plain; charset=utf-8',
        'sjson': 'application/json',
    }

    class TranscriptException(Exception):
        """
        When ?
        """
        pass


    class TranscriptConvertEx(Exception):
        """
        Raise when convertion fails.
        """
        pass


    class GetTranscriptFromYouTubeEx(Exception):
        """
        When ?
        """
        pass


    class TranscriptRequestValidationEx(Exception):
        """
        When ?
        """
        pass


    def __init__ (video_descriptor_instance):
        self.descriptor = video_descriptor_instance
        self.location = video_descriptor_instance.location


    @staticmethod
    def subs_filename(subs_id, lang='en'):
    """
    Generate proper filename for storage.
    """
    if lang == 'en':
        return u'subs_{0}.srt.sjson'.format(subs_id)
    else:
        return u'{0}_subs_{1}.srt.sjson'.format(lang, subs_id)


    @staticmethod
    def convert(content, input_format, output_format):
        """
        Convert transcript `content` from `input_format` to `output_format`.

        Accepted input formats: sjson, srt.
        Accepted output format: srt, txt, sjsons.
        """
        if input_format == output_format:
            return content
        elif input_format == 'srt':
            return SRT.convert_to(output_format, content, language???)
        elif input_format == 'sjson':
            return SJSON.convert_to('output_format', json.loads(content))
        else:
            raise Transcript.TranscriptConvertEx(_('Transcipt convertsion from {} to {] format is unsupported').format(
                input_format,
                output_format
            ))

    def get_asset_by_filename(self. filename):
        """
        Return asset by location and filename.
        """
        _ = self.descriptor.runtime.service(item, "i18n").ugettext
        try:
            contentstore().find(self.asset_location(filename))
        except NotFoundError as ex:
            log.info("Can't find content in storage for %s transcript.", filename)
            raise TranscriptException(_("{exception_message}: Can't find transcripts: {filename} in contentstore.").format(
                exception_message=ex.message,
                user_filename=filename
            ))

    def get_asset_by_subsid(self, subs_id, lang='en'):
        """
        Get asset from contentstore, asset location is built from subs_id and lang.
        """
        asset_filename = subs_filename(subs_id, lang)
        return self.get_asset_by_filename(self.location, asset_filename)

    def asset_location(self, filename):
        """
        Return asset location.
        """
        return StaticContent.compute_location(self.location.org, self.location.course, filename)

    def delete_asset(self, filename):
        """
        Delete asset by location and filename.
        """
        try:
            content = self.get_asset(filename)
            contentstore().delete(content.get_id())
            log.info("Transcript asset %s was removed from store.", filename)
        except NotFoundError:
            pass

    def delete_asset_by_subsid(self, subs_id, lang='en'):
        """
        Remove from store, if transcripts content exists.
        """
        filename = self.subs_filename(subs_id, lang)
        self.delete_asset(item.location, filename)


    def save_asset(content, content_name, mime_type):
        """
        Save named content to store. Returns location of saved content.
        """
        content_location = self.asset_location(content_name)
        content = StaticContent(content_location, content_name, mime_type, content)
        contentstore().save(content)
        return content_location


    def save_sjson_asset(sjson_content, subs_id, language='en'):
        """
        Save transcripts into `StaticContent`.

        Args:
        `subs_id`: str, subtitles id
        `language`: two chars str ('uk'), language of translation of transcripts

        Returns: location of saved subtitles.
        """
        filedata = json.dumps(sjson_content, indent=2)
        filename = self.subs_filename(subs_id, language)
        return self.save_asset(filedata, filename, 'application/json')

    def get_or_create_sjson_from_srt(self, subs_id, srt_filename, language):
        """
        Get sjson if already exists, otherwise generate it.

        Generate sjson with subs_id name, from user uploaded srt.
        Subs_id is extracted from srt filename, which was set by user.

        Raises:
            TranscriptException: when srt subtitles do not exist,
            and exceptions from generate_subs_from_source.

        `item` is module object.
        """
        try:
            sjson_transcript = self.get_asset_by_subsid(subs_id, language)
        except (TranscriptException):  # generating sjson from srt
            srt_transcripts = self.get_asset_by_filename(srt_filename)
            sjson_transcript = self.convert(srt_transcripts, 'srt', 'sjson')
            self.save_sjson_asset(sjson_transcript, subs_id, language)
        return sjson_transcript.data


