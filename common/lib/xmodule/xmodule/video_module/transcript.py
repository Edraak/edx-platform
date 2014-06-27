"""
Abstractions for trancripts.
"""
from . import srt, sjson


class TranscriptAsset(object):
    """
    Container for asset methods
    """
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
    mime_types = {
        'srt': 'application/x-subrip; charset=utf-8',
        'txt': 'text/plain; charset=utf-8',
        'sjson': 'application/json',
    }

    @staticmethod
    def convert(input_format, output_format):
        """
        Convert input_format to output format
        """
        result = getattr(
            globals().get(input_format.lower()),
            'convert_to_' + output_format.lower(),
            lambda x, *args, **kwargs: x
        )
        return result
