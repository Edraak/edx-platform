"""
Abstractions for trancript.
"""
import json
import logging

from xmodule.exceptions import NotFoundError
from xmodule.contentstore.django import contentstore
from xmodule.contentstore.content import StaticContent


log = logging.getLogger(__name__)


class TranscriptFormat(object):
    """
    Interface for transcript files.
    """
    def __init__(self, translation):
        """
        Args:
            `translation` is ugettext function.
            For example, item.runtime.service(item, "i18n").ugettext
        """
        self._ = translation

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

    class TranscriptConvertEx(Exception):
        """
        Raise when convertion fails.
        """
        pass


    class GetTranscriptFromYouTubeEx(Exception):
        """
        Raise when fetching transcript from YouTube is failed.
        """
        pass


    class TranscriptRequestValidationEx(Exception):
        """
        Raise when request is invalid.
        """
        pass


    def __init__ (self, video_descriptor_instance):
        self.descriptor = video_descriptor_instance
        self.location = video_descriptor_instance.location
        self._ = video_descriptor_instance.runtime.service(video_descriptor_instance, "i18n").ugettext


    @staticmethod
    def subs_filename(subs_id, lang='en'):
        """
        Generate proper filename for storage.
        """
        if lang == 'en':
            return u'subs_{0}.srt.sjson'.format(subs_id)
        else:
            return u'{0}_subs_{1}.srt.sjson'.format(lang, subs_id)

    def convert(self, content, input_format, output_format):
        """
        Convert transcript `content` from `input_format` to `output_format`.

        Accepted input formats: sjson, srt.
        Accepted output format: srt, txt, sjsons.
        """
        if input_format == output_format:
            return content
        elif input_format == 'srt':
            from .srt import Srt
            return Srt(self._).convert_to(output_format, content)
        elif input_format == 'sjson':
            from .sjson import Sjson
            return Sjson(self._).convert_to(output_format, content)
        else:
            raise Transcript.TranscriptConvertEx(self._('Transcipt convertsion from {} to {] format is unsupported').format(
                input_format,
                output_format
            ))

    def get_asset_by_filename(self, filename):
        """
        Return asset by location and filename.
        """
        return contentstore().find(self.asset_location(filename))

    def get_asset_by_subsid(self, subs_id, lang='en'):
        """
        Get asset from contentstore, asset location is built from subs_id and lang.
        """
        asset_filename = self.subs_filename(subs_id, lang)
        return self.get_asset_by_filename(asset_filename)

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


    def save_asset(self, content, content_name, mime_type):
        """
        Save named content to store. Returns location of saved content.
        """
        content_location = self.asset_location(content_name)
        content = StaticContent(content_location, content_name, mime_type, content)
        contentstore().save(content)
        return content_location


    def save_sjson_asset(self, sjson_content, subs_id, language='en'):
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
            self.TranscriptEx: when srt subtitles do not exist,
            and exceptions from generate_subs_from_source.

        `item` is module object.
        """
        try:
            sjson_transcript = self.get_asset_by_subsid(subs_id, language)
        except (NotFoundError):  # generating sjson from srt
            srt_transcript = self.get_asset_by_filename(srt_filename)
            sjson_content = self.convert(srt_transcript.data, 'srt', 'sjson')
            self.save_sjson_asset(sjson_content, subs_id, language)
        return sjson_content


