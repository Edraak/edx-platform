# -*- coding: utf-8 -*-

"""
Acceptance tests for Video.
"""

from unittest import skip

from .helpers import UniqueCourseTest, load_data_str
from ..pages.lms.video import VideoPage
from ..pages.lms.tab_nav import TabNavPage
from ..pages.lms.course_nav import CourseNavPage
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


class VideoTestA(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestA, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video')
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_stores_position_correctly(self):
        """
        Tests that Video component stores position correctly when page is reloaded Given the course has a
        Video component in "Youtube" mode.
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

        # click video button "play"
        self.video.click_player_button('play')

        # seek video to "10" seconds
        self.video.seek_video(10)

        # click video button "pause"
        self.video.click_player_button('pause')

        # reload the page
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # click video button "play"
        self.video.click_player_button('play')

        # video starts playing from "0:10" position
        self.assertEqual(self.video.get_video_position, '0:10')

    def test_video_component_rendered_in_youtube_without_html5_sources(self):
        """
        Tests that Video component is rendered in Youtube mode without HTML5 sources Given the course
        has a Video component in "Youtube" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_video_aligned_correctly_if_transcript_hidden_in_full_screen(self):
        """
        Tests that Video is aligned correctly if transcript is hidden in fullscreen mode
        Given the course has a Video component in "Youtube" mode.
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if is video aligned correctly without enabled transcript
        self.assertTrue(self.video.is_aligned(False))


class VideoTestB(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestB, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_fully_rendered_in_youtube_with_html5_sources(self):
        """
        Tests that Video component is fully rendered in Youtube mode with HTML5 sources Given the course
        has a Video component in "Youtube_HTML5" mode.
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_video_component_not_rendered_in_youtube_with_html5_sources(self):
        """
        Tests that Video component is not rendered in Youtube mode with HTML5 sources Given the course
        has a Video component in "Youtube_HTML5" mode.
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "Youtube" mode
        self.assertTrue(self.video.is_video_rendered('html5'))


class VideoTestC(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestC, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_fully_rendered_in_html5_mode(self):
        """
        Tests that Video component is fully rendered in HTML5 mode Given the course has a Video component
        in "HTML5" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "HTML5" mode
        self.assertTrue(self.video.is_video_rendered('html5'))

        # check if all sources are correct. It means page has video source urls that match exactly with `HTML5_SOURCES`
        self.assertEqual(self.video.get_all_video_sources, HTML5_SOURCES)

    def test_autoplay_disabled_for_video_component(self):
        """
        Tests that Autoplay is disabled in for a Video component Given the course has a Video component in HTML5 mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if the video has autoplay mode disabled
        self.assertFalse(self.video.is_autoplay_enabled)


class VideoTestD(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestD, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'html5_sources': HTML5_SOURCES_INCORRECT
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_rendered_in_youtube_with_unsupported_html5_sources(self):
        """
        Tests that Video component is rendered in Youtube mode with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "Youtube_HTML5_Unsupported_Video" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if video has rendered in "youtube" mode
        self.assertTrue(self.video.is_video_rendered('youtube'))

    def test_video_component_rendered_in_html5_with_unsupported_html5_sources(self):
        """
        Tests that Video component is rendered in HTML5 mode with HTML5 sources that doesn't supported by browser
        Given the course has a Video component in "HTML5_Unsupported_Video" mode
        """

        # Navigate to a video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if error message is shown
        self.assertTrue(self.video.is_error_message_shown)

        # check if error message has correct text
        correct_error_message_text = 'ERROR: No playable video sources found!'
        self.assertIn(correct_error_message_text, self.video.get_error_message_text)


class VideoTestE(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestE, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        html5_metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'A')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-1').add_children(
                        XBlockFixtureDesc('video', 'B')
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-2').add_children(
                        XBlockFixtureDesc('video', 'C', metadata=html5_metadata)
        )

                ))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_component_stores_speed_correctly_for_multiple_videos(self):
        """
        Tests that Video component stores speed correctly when each video is in separate sequence
        Given it has
            a video "A" in "Youtube" mode in position "1" of sequential
            a video "B" in "Youtube" mode in position "2" of sequential
            a video "C" in "HTML5" mode in position "3" of sequential
        """

        # open the section with videos
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # select the "2.0" speed on video "A"
        self.course_nav.go_to_sequential('A')
        self.video.change_speed('2.0')

        # select the "0.50" speed on video "B"
        self.course_nav.go_to_sequential('B')
        self.video.change_speed('2.0')

        # open video "C"
        self.course_nav.go_to_sequential('C')

        # check if video "C" should start playing at speed "0.75"
        self.assertEqual(self.video.get_video_speed, '0.75x')

        # open video "A"
        self.course_nav.go_to_sequential('A')

        # check if video "A" should start playing at speed "2.0"
        self.assertEqual(self.video.get_video_speed, '2.0x')

        # reload the page
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # open video "A"
        self.course_nav.go_to_sequential('A')

        # check if video "A" should start playing at speed "2.0"
        self.assertEqual(self.video.get_video_speed, '2.0x')

        # select the "1.0" speed on video "A"
        self.video.change_speed('1.0')

        # open video "B"
        self.course_nav.go_to_sequential('B')

        # check if video "B" should start playing at speed "0.50"
        self.assertEqual(self.video.get_video_speed, '0.50x')

        # open video "C"
        self.course_nav.go_to_sequential('C')

        # check if video "C" should start playing at speed "1.0"
        self.assertEqual(self.video.get_video_speed, '1.0x')


class VideoTestF(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestF, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )


        metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES,
            'transcripts': {'zh': 'chinese_transcripts.srt'}
        }

        # from nose.tools import set_trace; set_trace()
        course_fix.add_asset('chinese_transcripts.srt')

        # from nose.tools import set_trace; set_trace()
        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()


        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_cc_button_works_correctly_without_english_transcript_html5_mode(self):
        """
        Tests that CC button works correctly w/o english transcript in HTML5 mode of Video component
        Given I have a "chinese_transcripts.srt" transcript file in assets And it has a video in "HTML5" mode.
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        from nose.tools import set_trace; set_trace()

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if we see "好 各位同学" text in the captions
        self.assertIn("好 各位同学", self.video.captions_text)


class VideoTestG(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestG, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'youtube_id_1_0': '',
            'youtube_id_0_75': '',
            'youtube_id_1_25': '',
            'youtube_id_1_5': '',
            'html5_sources': HTML5_SOURCES,
            'sub': 'OEoXaMPEzfM'
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_cc_button_works_correctly_only_with_english_transcript(self):
        """
        Tests that CC button works correctly only w/ english transcript in HTML5 mode of Video component
        Given I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets And it has a video in "HTML5" mode.
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if we see "Hi, welcome to Edx." text in the captions
        self.assertIn("Hi, welcome to Edx.", self.video.captions_text)

    def test_video_aligned_correctly_if_transcript_visible_in_full_screen(self):
        """
        Tests that Video is aligned correctly if transcript is visible in fullscreen mode Given I have a
        "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets And it has a video in "HTML5" mode:
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if video aligned correctly with enabled transcript
        self.assertTrue(self.video.is_aligned(True))


class VideoTestH(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestH, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'transcripts': {'zh': 'chinese_transcripts.srt'}
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_cc_button_works_correctly_without_english_transcript_youtube_mode(self):
        """
        Tests that CC button works correctly w/o english transcript in Youtube mode of Video component
        Given I have a "chinese_transcripts.srt" transcript file in assets And it has a video in "Youtube" mode.
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if we see "好 各位同学" text in the captions
        self.assertIn("好 各位同学", self.video.captions_text)


class VideoTestI(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestI, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        metadata = {
            'sub': 'OEoXaMPEzfM'
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_video_aligned_correctly_on_transcript_toggle_in_fullscreen(self):
        """
        Tests that Video is aligned correctly on transcript toggle in fullscreen mode Given I have a
        "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets And it has a video in "Youtube" mode.
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # click video button "fullscreen"
        self.video.click_player_button('fullscreen')

        # check if video aligned correctly with enabled transcript
        self.assertTrue(self.video.is_aligned(True))

        # click video button "CC"
        self.video.click_player_button('CC')

        # check if video aligned correctly without enabled transcript
        self.assertTrue(self.video.is_aligned(False))


class VideoTestJ(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestJ, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        youtube_ab_metadata = {
            'sub': 'OEoXaMPEzfM',
            'download_track': True
        }

        youtube_c_metadata = {
            'track': 'http://example.org/',
            'download_track': True
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'A', metadata=youtube_ab_metadata)
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-1').add_children(
                        XBlockFixtureDesc('video', 'B', metadata=youtube_ab_metadata)
        ),
                    XBlockFixtureDesc('vertical', 'Test Vertical-2').add_children(
                        XBlockFixtureDesc('video', 'C', metadata=youtube_c_metadata)
        )

                ))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_download_transcript_button_works_correctly(self):
        """
        Tests that Download Transcript button works correctly in Video component
        Given
           I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
           it has a video "A" in "Youtube" mode in position "1" of sequential
           And a video "B" in "Youtube" mode in position "2" of sequential
           And a video "C" in "Youtube" mode in position "3" of sequential
        """

        # open the section with videos
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if we can download transcript in "srt" format that has text "00:00:00,270"
        self.assertTrue(self.video.can_we_download_transcript('srt', '00:00:00,270'))

        # select the transcript format "txt"
        self.assertTrue(self.video.select_transcript_format('txt'))

        # check if wwe can download transcript in "txt" format that has text "Hi, welcome to Edx."
        self.assertTrue(self.video.can_we_download_transcript('txt', 'Hi, welcome to Edx.'))

        # open video "B"
        self.course_nav.go_to_sequential('B')

        # check if we can download transcript in "txt" format that has text "Hi, welcome to Edx."
        self.assertTrue(self.video.can_we_download_transcript('txt', 'Hi, welcome to Edx.'))

        # open video "C"
        self.course_nav.go_to_sequential('C')

        # menu "download_transcript" doesn't exist
        self.assertFalse(self.video.is_menu_exist('download_transcript'))

class VideoTestK(UniqueCourseTest):

    def setUp(self):
        """
        Initialize pages and install a course fixture.
        """
        super(VideoTestK, self).setUp()

        self.video = VideoPage(self.browser)
        self.tab_nav = TabNavPage(self.browser)
        self.course_nav = CourseNavPage(self.browser)
        self.course_info_page = CourseInfoPage(self.browser, self.course_id)

        # Install a course fixture with a video component
        course_fix = CourseFixture(
            self.course_info['org'], self.course_info['number'],
            self.course_info['run'], self.course_info['display_name']
        )

        youtube_metadata = {
            'youtube_id_1_5': 'b7xgknqkQk8',
            'sub': 'OEoXaMPEzfM'
        }

        course_fix.add_children(
            XBlockFixtureDesc('chapter', 'Test Chapter').add_children(
                XBlockFixtureDesc('sequential', 'Test Section').add_children(
                    XBlockFixtureDesc('vertical', 'Test Vertical-0').add_children(
                        XBlockFixtureDesc('video', 'Video', metadata=youtube_metadata)
        )))).install()

        # Auto-auth register for the course
        AutoAuthPage(self.browser, course_id=self.course_id).visit()

    def test_youtube_video_has_correct_transcript(self):
        """
        Tests that Youtube video has correct transcript if fields for other speeds are filled.
        Given
             I have a "subs_OEoXaMPEzfM.srt.sjson" transcript file in assets
             I have a "subs_b7xgknqkQk8.srt.sjson" transcript file in assets
             it has a video in "Youtube" mode
        """

        # go to video
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # make sure captions are opened
        self.video.set_captions_visibility_state('opened')

        # check if "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

        # select the "1.50" speed
        self.video.change_speed('1.50')

        # reload the page
        self.course_info_page.visit()
        self.tab_nav.go_to_tab('Courseware')

        # check if "Hi, welcome to Edx." text in the captions
        self.assertIn('Hi, welcome to Edx.', self.video.captions_text)

        # check if duration is "1:00"
        self.assertTrue(self.video.is_duration_matches('1:00'))
