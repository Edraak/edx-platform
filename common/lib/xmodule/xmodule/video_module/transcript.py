"""
Abstractions for trancripts.
"""
from srt import Srt
from sjson import Sjson


class TranscriptConvertEx(Exception):
    """
    Raise when convertion from one format to another fails.
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


class TranscriptAsset(obect):
    """
    Container for asset methods
    """
    mime_types = {
        'srt': 'application/x-subrip; charset=utf-8',
        'txt': 'text/plain; charset=utf-8',
        'sjson': 'application/json',
    }

    @staticmethod
    def asset(location, subs_id, lang='en', filename=None):
        """
        Get asset from contentstore, asset location is built from subs_id and lang.

        `location` is module location.
        """
        asset_filename = subs_filename(subs_id, lang) if not filename else filename
        return Transcript.get_asset(location, asset_filename)

    @staticmethod
    def get_asset(location, filename):
        """
        Return asset by location and filename.
        """
        return contentstore().find(Transcript.asset_location(location, filename))

    @staticmethod
    def asset_location(location, filename):
        """
        Return asset location. `location` is module location.
        """
        return StaticContent.compute_location(location.course_key, filename)

    @staticmethod
    def delete_asset(location, filename):
        """
        Delete asset by location and filename.
        """
        try:
            content = Transcript.get_asset(location, filename)
            contentstore().delete(content.get_id())
            log.info("Transcript asset %s was removed from store.", filename)
        except NotFoundError:
            pass
        return StaticContent.compute_location(location.course_key, filename)


class Transcript(TranscriptAsset):
    """
    Container for method of transcript format files.
    """
    def __init__(self, transcript_type, translation=lambda x: x):
        """
        Args:
            `translation` is ugettext function.
            For example, item.runtime.service(item, "i18n").ugettext
            transcript_type, str: type of transcript format class: 'srt' or 'sjson'
        """
        self._ = translation
        self.format_container = getattr(module, transcript_format)()

    def convert_to(output_format, content):
        """
        Convert content from current format to output format
        """
        return getattr(
            self.format_container,
            'convert_to' + output_format.lower(),
            lambda x: raise TranscriptConvertEx(
                self._("Transcript convertion from {} to {} format is not supported").format(
                    self.transcript_class.__name__,
                    output_format
                )
            )
        )(self._prepare_content(self._content))

    @property
    def mime_type(self):
        """
        Return mime type.
        """
        return self.format_container.mime_type

