# -*- coding: utf-8 -*-
""" Tests for transcripts_utils. """
import unittest
from uuid import uuid4
import copy
import textwrap
from mock import patch, Mock

from pymongo import MongoClient

from django.test.utils import override_settings
from django.conf import settings
from django.utils import translation

from nose.plugins.skip import SkipTest

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.contentstore.content import StaticContent
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.exceptions import NotFoundError
from xmodule.contentstore.django import contentstore, _CONTENTSTORE
from xmodule.video_module import transcripts_utils
from xmodule.video_module.transcript import Transcript

from contentstore.tests.modulestore_config import TEST_MODULESTORE
TEST_DATA_CONTENTSTORE = copy.deepcopy(settings.CONTENTSTORE)
TEST_DATA_CONTENTSTORE['DOC_STORE_CONFIG']['db'] = 'test_xcontent_%s' % uuid4().hex


@override_settings(CONTENTSTORE=TEST_DATA_CONTENTSTORE, MODULESTORE=TEST_MODULESTORE)
class TestDownloadYoutubeSubs(ModuleStoreTestCase):
    """Tests for `download_youtube_subs` function."""

    def test_success_downloading_subs(self):
        response = textwrap.dedent("""<?xml version="1.0" encoding="utf-8" ?>
                <transcript>
                    <text start="0" dur="0.27"></text>
                    <text start="0.27" dur="2.45">Test text 1.</text>
                    <text start="2.72">Test text 2.</text>
                    <text start="5.43" dur="1.73">Test text 3.</text>
                </transcript>
        """)
        good_youtube_id = 'good_id_1'

        with patch('xmodule.video_module.transcripts_utils.requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=response, content=response)
            subs = transcripts_utils.get_transcripts_from_youtube(good_youtube_id, settings, Mock())
            self.assertDictEqual(
                subs,
                {'end': [2720, 2720, 7160], 'start': [270, 2720, 5430], 'text': ['Test text 1.', 'Test text 2.', 'Test text 3.']})

        mock_get.assert_any_call('http://video.google.com/timedtext', params={'lang': 'en', 'v': 'good_id_1'})

    @patch('xmodule.video_module.transcripts_utils.requests.get')
    def test_fail_downloading_subs(self, mock_get):

        mock_get.return_value = Mock(status_code=404, text='Error 404')

        bad_youtube_id  = 'BAD_YOUTUBE_ID1',

        with self.assertRaises(Transcript.GetTranscriptFromYouTubeEx):
            transcripts_utils.get_transcripts_from_youtube(bad_youtube_id, settings, Mock())

    def test_success_downloading_chinese_transcripts(self):

        # Disabled 11/14/13
        # This test is flakey because it performs an HTTP request on an external service
        # Re-enable when `requests.get` is patched using `mock.patch`
        raise SkipTest

        good_youtube_subs_chinese = 'j_jEn79vS3g'  # Chinese, utf-8

        # Check Transcript.GetTranscriptFromYouTubeEx not thrown
        transcripts_utils.download_youtube_subs(good_youtube_subs_chinese, settings, Mock())


class TestYoutubeTranscripts(unittest.TestCase):
    """
    Tests for checking right datastructure returning when using youtube api.
    """
    @patch('xmodule.video_module.transcripts_utils.requests.get')
    def test_youtube_bad_status_code(self, mock_get):
        mock_get.return_value = Mock(status_code=404, text='test')
        youtube_id = 'bad_youtube_id'
        with self.assertRaises(Transcript.GetTranscriptFromYouTubeEx):
            transcripts_utils.get_transcripts_from_youtube(youtube_id, settings, translation)

    @patch('xmodule.video_module.transcripts_utils.requests.get')
    def test_youtube_empty_text(self, mock_get):
        mock_get.return_value = Mock(status_code=200, text='')
        youtube_id = 'bad_youtube_id'
        with self.assertRaises(Transcript.GetTranscriptFromYouTubeEx):
            transcripts_utils.get_transcripts_from_youtube(youtube_id, settings, translation)

    def test_youtube_good_result(self):
        response = textwrap.dedent("""<?xml version="1.0" encoding="utf-8" ?>
                <transcript>
                    <text start="0" dur="0.27"></text>
                    <text start="0.27" dur="2.45">Test text 1.</text>
                    <text start="2.72">Test text 2.</text>
                    <text start="5.43" dur="1.73">Test text 3.</text>
                </transcript>
        """)
        expected_transcripts = {
            'start': [270, 2720, 5430],
            'end': [2720, 2720, 7160],
            'text': ['Test text 1.', 'Test text 2.', 'Test text 3.']
        }
        youtube_id = 'good_youtube_id'
        with patch('xmodule.video_module.transcripts_utils.requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=response, content=response)
            transcripts = transcripts_utils.get_transcripts_from_youtube(youtube_id, settings, translation)
        self.assertEqual(transcripts, expected_transcripts)
        mock_get.assert_called_with('http://video.google.com/timedtext', params={'lang': 'en', 'v': 'good_youtube_id'})
