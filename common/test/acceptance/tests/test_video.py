# -*- coding: utf-8 -*-

"""
Acceptance tests for Video.
"""

from unittest import skip
from .helpers import UniqueCourseTest
from ..pages.lms.video import VideoPage
from ..pages.lms.tab_nav import TabNavPage
from ..pages.studio.auto_auth import AutoAuthPage
from ..pages.lms.course_info import CourseInfoPage
from ..fixtures.course import CourseFixture, XBlockFixtureDesc


HTML5_SOURCES = [
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.mp4',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.webm',
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.ogv',
]

HTML5_SOURCES_INCORRECT = [
    'https://s3.amazonaws.com/edx-course-videos/edx-intro/edX-FA12-cware-1_100.mp99',
]

HTML5_METADATA = {
    'youtube_id_1_0': '',
    'youtube_id_0_75': '',
    'youtube_id_1_25': '',
    'youtube_id_1_5': '',
    'html5_sources': HTML5_SOURCES
}

YT_HTML5_METADATA = {
    'html5_sources': HTML5_SOURCES
}

class VideoBaseTest(UniqueCourseTest):
    """
    Base class for tests of the Video Player
    Sets up the course and provides helper functions for the Video tests.
    """

    def setUp(self):
        """
        Initialization of pages and course fixture for video tests
        """
        super(VideoBaseTest, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        self.course_fixture = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        self.metadata = {}
        self.transcript = None
        self.verticals = None
        self.xblock_videos = None

    def navigate_to_video(self):
        """ Prepare the course and get to the video and render it """
        self._install_course_fixture()
        self._navigate_to_courseware_video_and_render()

    def navigate_to_video_no_render(self):
        """
        Prepare the course and get to the video unit
        however do not wait for it to render, because
        the has been an error.
        """
        self._install_course_fixture()
        self._navigate_to_courseware_video_no_render()

    def _install_course_fixture(self):
        """ Install the course fixture that has been defined """
        if self.transcript:
            self.course_fixture.add_asset(self.transcript)

        self.course_fixture.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                self._videos()
                )).install()

    def _videos(self):

        # If you are not sending any metadata then `None` should be send as metadata to XBlockFixtureDesc
        # instead of empty dictionary otherwise test will not produce correct results.
        _metadata = self.metadata if self.metadata else None

        if self.xblock_videos is None:
            return XBlockFixtureDesc('sequential', 'Test Section').add_children(
                XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                XBlockFixtureDesc('video', 'Video', metadata=_metadata)
            ))
        else:
            return self.xblock_videos

    # def _install_course_fixture(self):
    #     """ Install the course fixture that has been defined """
    #     if self.transcript:
    #         self.course_fixture.add_asset(self.transcript)
    #
    #     chapter_sequential = XBlockFixtureDesc('sequential', 'Test Section')
    #     chapter_sequential.add_children(*self._add_course_verticals())
    #     chapter = XBlockFixtureDesc('chapter', 'Test Chapter').add_children(chapter_sequential)
    #     self.course_fixture.add_children(chapter)
    #     self.course_fixture.install()

    def _add_course_verticals(self):
        xblock_verticals = []
        verticals = self.verticals

        if not verticals:
            # If you are not sending any metadata then `None` should be send as metadata to XBlockFixtureDesc
            # instead of empty dictionary otherwise test will not produce correct results.
            _metadata = self.metadata if self.metadata else None
            verticals = [[['Video', _metadata]]]

        for vertical_index, vertical in enumerate(verticals):
            xblock_verticals.append(self._create_vertical(vertical, vertical_index))
        return xblock_verticals

    def _create_vertical(self, vertical, vertical_index):
        xblock_vertical = XBlockFixtureDesc('vertical', 'Test Vertical-{0}'.format(vertical_index))

        for videos in vertical:

            if len(videos) == 1:
                xblock_vertical.add_children(XBlockFixtureDesc('video', videos[0]))
            else:
                xblock_vertical.add_children(XBlockFixtureDesc('video', videos[0], metadata=videos[1]))

        return xblock_vertical


    def _navigate_to_courseware_video(self):
        """ Register for the course and navigate to the video unit """
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

    def _navigate_to_courseware_video_and_render(self):
        """ Wait for the video player to render """
        self._navigate_to_courseware_video()
        self.video.wait_for_video_player_render()

    def _navigate_to_courseware_video_no_render(self):
        """ Wait for the video Xmodule but not for rendering """
        self._navigate_to_courseware_video()
        self.video.wait_for_video_class()


class YouTubeVideoTest(VideoBaseTest):
    """ Test YouTube Video Player """

    def setUp(self):
        super(YouTubeVideoTest, self).setUp()

    def test_video_component_rendered_in_youtube_without_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in Youtube mode without HTML5 sources
        Given the course has a Video component in "Youtube" mode
        Then the video has rendered in "Youtube" mode
        """
        self.navigate_to_video()

        # Verify that video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_cc_button_without_english_transcript_youtube_mode(self):
        """
        Scenario: CC button works correctly w/o english transcript in Youtube mode of Video component
        Given the course has a Video component in "Youtube" mode
        And I have defined a non-english transcript for the video
        And I have uploaded a non-english transcript file to assets
        Then I see the correct text in the captions
        """
        self.metadata['transcripts'] = {'zh': 'chinese_transcripts.srt'}
        self.transcript = 'chinese_transcripts.srt'
        self.navigate_to_video()
        self.video.show_captions()

        # Verify that we see "好 各位同学" text in the captions
        unicode_text = "好 各位同学".decode('utf-8')
        self.assertIn(unicode_text, self.video.captions_text)

    def test_cc_button_transcripts_and_sub_fields_empty(self):
        """
        Scenario: CC button works correctly if transcripts and sub fields are empty,
        but transcript file exists in assets (Youtube mode of Video component)
        Given the course has a Video component in "Youtube" mode
        And I have uploaded a .srt.sjson file to assets
        Then I see the correct english text in the captions
        """
        self.transcript = 'subs_OEoXaMPEzfM.srt.sjson'
        self.navigate_to_video()
        self.video.show_captions()

        # Verify that we see "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

    def test_cc_button_hidden_if_no_translations(self):
        """
        Scenario: CC button is hidden if no translations
        Given the course has a Video component in "Youtube" mode
        Then the "CC" button is hidden
        """
        self.navigate_to_video()
        self.assertFalse(self.video.is_button_shown('CC'))


class YouTubeHtml5VideoTest(VideoBaseTest):
    """ Test YouTube HTML5 Video Player """

    def setUp(self):
        super(YouTubeHtml5VideoTest, self).setUp()
        self.metadata = YT_HTML5_METADATA

    def test_video_component_rendered_in_youtube_with_unsupported_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in Youtube mode
            with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "Youtube_HTML5_Unsupported_Video" mode
        Then the video has rendered in "Youtube" mode
        """
        self.metadata['html5_sources'] = HTML5_SOURCES_INCORRECT
        self.navigate_to_video()

        # Verify that the video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))


class Html5VideoTest(VideoBaseTest):
    """ Test HTML5 Video Player """

    def setUp(self):
        super(Html5VideoTest, self).setUp()
        self.metadata = HTML5_METADATA

    def test_autoplay_disabled_for_video_component(self):
        """
        Scenario: Autoplay is disabled in LMS for a Video component
        Given the course has a Video component in "HTML5" mode
        Then it does not have autoplay enabled
        """
        self.navigate_to_video()

        # Verify that the video has autoplay mode disabled
        self.assertFalse(self.video.is_autoplay_enabled)

    def test_video_component_rendered_in_html5_with_unsupported_html5_sources(self):
        """
        Scenario: Video component is rendered in the LMS in HTML5 mode with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "HTML5_Unsupported_Video" mode
        Then error message is shown
        And error message has correct text
        """
        self.metadata['html5_sources'] = HTML5_SOURCES_INCORRECT
        self.navigate_to_video_no_render()

        # Verify that error message is shown
        self.assertTrue(self.video.is_error_message_shown)

        # Verify that error message has correct text
        correct_error_message_text = 'ERROR: No playable video sources found!'
        self.assertIn(correct_error_message_text, self.video.error_message_text)

    @skip('incomplete')
    def test_video_component_stores_speed_correctly_for_multiple_videos(self):
        """
        Scenario: Video component stores speed correctly when each video is in separate sequence
        Given it has
            a video "A" in "Youtube" mode in position "1" of sequential
            a video "B" in "Youtube" mode in position "2" of sequential
            a video "C" in "HTML5" mode in position "3" of sequential
        """

        self.xblock_videos = XBlockFixtureDesc('sequential', 'Test Section').add_children(
            XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'A')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-1').add_children(
                        XBlockFixtureDesc('video', 'B')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-2').add_children(
                        XBlockFixtureDesc('video', 'C', metadata=HTML5_METADATA)
        ))

        self.verticals = [[['A']], [['B']], [['C', HTML5_METADATA]]]

        self.navigate_to_video()

        from nose.tools import set_trace; set_trace()

        # # select the "2.0" speed on video "A"
        # self.course_nav.go_to_sequential('A')
        # self.video.change_speed('2.0')
        #
        # # select the "0.50" speed on video "B"
        # self.course_nav.go_to_sequential('B')
        # self.video.change_speed('0.50')
        #
        # # open video "C"
        # self.course_nav.go_to_sequential('C')
        #
        # #self.video.wait_for_video_player()
        #
        # # check if video "C" should start playing at speed "0.75"
        # self.assertEqual(self.video.get_video_speed, '0.75x')
        #
        # # open video "A"
        # self.course_nav.go_to_sequential('A')
        #
        # # check if video "A" should start playing at speed "2.0"
        # self.assertEqual(self.video.get_video_speed, '2.0x')
        #
        # # reload the page
        # self.video.reload_page()
        #
        # self.video.wait_for_video_player()
        #
        # # open video "A"
        # self.course_nav.go_to_sequential('A')
        #
        # # check if video "A" should start playing at speed "2.0"
        # self.assertEqual(self.video.get_video_speed, '2.0x')
        #
        # # select the "1.0" speed on video "A"
        # self.video.change_speed('1.0')
        #
        # # open video "B"
        # self.course_nav.go_to_sequential('B')
        #
        # # check if video "B" should start playing at speed "0.50"
        # self.assertEqual(self.video.get_video_speed, '0.50x')
        #
        # # open video "C"
        # self.course_nav.go_to_sequential('C')
        #
        # # check if video "C" should start playing at speed "1.0"
        # self.assertEqual(self.video.get_video_speed, '1.0x')
