"""
Container for video module and it's utils.
"""

# Disable wildcard-import warnings.
# pylint: disable=W0401

class TranscriptException(Exception):  # pylint disable=C0111
    pass


class TranscriptsGenerationException(Exception):  # pylint disable=C0111
    pass


class GetTranscriptsFromYouTubeException(Exception):  # pylint disable=C0111
    pass


class TranscriptsRequestValidationException(Exception):  # pylint disable=C0111
    pass


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


from .transcripts_utils import *
from .video_utils import *
from .video_module import *
