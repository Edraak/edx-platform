"""
Abstractions for trancripts.
"""
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


class TranscriptFormat(object):
    """
    Interface for transcript format files.
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
        return getattr(
            self,
            'convert_to' + output_format.lower(),
            lambda x: raise TranscriptConvertEx(
                self._("Transcript convertion from {} to {} format is not supported").format(
                    self.class.name,
                    output_format
                )
            )
        )(self._prepare_content(content))
