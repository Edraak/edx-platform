"""
Video player in the courseware.
"""

from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise, Promise
from bok_choy.javascript import wait_for_js, js_defined


VIDEO_BUTTONS = {
    'CC': '.hide-subtitles',
    'volume': '.volume',
    'play': '.video_control.play',
    'pause': '.video_control.pause',
    'fullscreen': '.add-fullscreen',
    'download_transcript': '.video-tracks > a',
}

VIDEO_MENUS = {
    'language': '.lang .menu',
    'speed': '.speed .menu',
    'download_transcript': '.video-tracks .a11y-menu-list',
}


@js_defined('window.Video', 'window.RequireJS.require', 'window.jQuery')
class VideoPage(PageObject):
    """
    Video player in the courseware.
    """

    url = None

    @wait_for_js
    def is_browser_on_page(self):
        return self.q(css='div.xmodule_VideoModule').present

    def wait_for_ajax(self):
        """ Make sure that all ajax requests are finished. """
        def _is_ajax_finished():
            return self.browser.execute_script("return jQuery.active") == 0

        EmptyPromise(_is_ajax_finished, "Finished waiting for ajax requests.").fulfill()

    @wait_for_js
    def wait_for_video_class(self):
        """
        Wait until Video Player Rendered Completely.
        """
        video_css = 'div.video'

        self.wait_for_ajax()
        return EmptyPromise(lambda: self.q(css=video_css).present, "Video is initialized").fulfill()

    @wait_for_js
    def wait_for_video_player_render(self):
        """
        Wait until Video Player Rendered Completely.
        """
        def _is_finished_loading():
            return not self.q(css='.video-wrapper .spinner').visible

        self.wait_for_video_class()
        return EmptyPromise(_is_finished_loading, 'Finished loading the video', try_limit=10, timeout=60,
                            try_interval=10).fulfill()

    def is_video_rendered(self, mode):
        """
        Check that if video is rendered in `mode`.
        :param mode: Video mode, `html5` or `youtube`
        """
        modes = {
            'html5': 'video',
            'youtube': 'iframe'
        }

        html_tag = modes[mode]
        css = '.video {0}'.format(html_tag)

        EmptyPromise(lambda: self.q(css=css).present,
                     'Video Rendering Failed in {0} mode.'.format(mode)).fulfill()

        return self.q(css='.speed_link').present

    @property
    def all_video_sources(self):
        """
        Extract all video source urls on current page.
        """
        return self.q(css='.video-player video source').map(lambda el: el.get_attribute('src').split('?')[0]).results

    @property
    def is_autoplay_enabled(self):
        """
        Extract `data-autoplay` attribute to check video autoplay is enabled or disabled.
        """
        auto_play = self.q(css='.video').attrs('data-autoplay')[0]

        if auto_play.lower() == 'false':
            return False

        return True

    @property
    def is_error_message_shown(self):
        """
        Checks if video player error message shown.
        :return: bool
        """
        return self.q(css='.video .video-player h3').visible

    @property
    def error_message_text(self):
        """
        Extract video player error message text.
        :return: str
        """
        return self.q(css='.video .video-player h3').text[0]

    @property
    def is_CC_button_shown(self):
        return self.q(css='.hide-subtitles').visible

    @wait_for_js
    def show_captions(self):
        """
        Show the video captions.
        """
        def _is_subtitles_open():
            is_open = not self.q(css='.closed .subtitles').present
            return is_open

        # Make sure that the CC button is there
        EmptyPromise(lambda: self.is_CC_button_shown,
            "CC button is shown").fulfill()

        # Check if the captions are already open and click if not
        if _is_subtitles_open() is False:
            self.q(css='.hide-subtitles').first.click()

        # Verify that they are now open
        EmptyPromise(_is_subtitles_open,
            "Subtitles are shown").fulfill()

    @property
    def captions_text(self):
        """
        Extract captions text.
        :return: str
        """
        def _captions_text():
            is_present = self.q(css='.subtitles').present
            result = None

            if is_present:
                result = self.q(css='.subtitles').text[0]

            return is_present, result

        return Promise(_captions_text, 'Captions Text').fulfill()
