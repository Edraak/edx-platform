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

from contentstore.tests.modulestore_config import TEST_MODULESTORE
TEST_DATA_CONTENTSTORE = copy.deepcopy(settings.CONTENTSTORE)
TEST_DATA_CONTENTSTORE['DOC_STORE_CONFIG']['db'] = 'test_xcontent_%s' % uuid4().hex


@override_settings(CONTENTSTORE=TEST_DATA_CONTENTSTORE, MODULESTORE=TEST_MODULESTORE)
class TestSaveAsset(ModuleStoreTestCase):
    """Tests for `save_subs_to_store` function."""

    org = 'MITx'
    number = '999'
    display_name = 'Test course'

    def clear_subs_content(self):
        """Remove, if subtitles content exists."""
        try:
            content = contentstore().find(self.content_location)
            contentstore().delete(content.get_id())
        except NotFoundError:
            pass

    def setUp(self):

        self.course = CourseFactory.create(
            org=self.org, number=self.number, display_name=self.display_name)

        self.subs = {
            'start': [100, 200, 240, 390, 1000],
            'end': [200, 240, 380, 1000, 1500],
            'text': [
                'subs #1',
                'subs #2',
                'subs #3',
                'subs #4',
                'subs #5'
            ]
        }

        self.subs_id = str(uuid4())
        filename = 'subs_{0}.srt.sjson'.format(self.subs_id)
        self.content_location = StaticContent.compute_location(
            self.org, self.number, filename
        )

        # incorrect  subs
        self.unjsonable_subs = set([1])  # set can't be serialized

        self.unjsonable_subs_id = str(uuid4())
        filename_unjsonable = 'subs_{0}.srt.sjson'.format(self.unjsonable_subs_id)
        self.content_location_unjsonable = StaticContent.compute_location(
            self.org, self.number, filename_unjsonable
        )

        self.clear_subs_content()

    def test_save_subs_to_store(self):
        with self.assertRaises(NotFoundError):
            contentstore().find(self.content_location)

        result_location = transcripts_utils.save_subs_to_store(
            self.subs,
            self.subs_id,
            self.course)

        self.assertTrue(contentstore().find(self.content_location))
        self.assertEqual(result_location, self.content_location)

    def test_save_unjsonable_subs_to_store(self):
        """
        Assures that subs, that can't be dumped, can't be found later.
        """
        with self.assertRaises(NotFoundError):
            contentstore().find(self.content_location_unjsonable)

        with self.assertRaises(TypeError):
            transcripts_utils.save_subs_to_store(
                self.unjsonable_subs,
                self.unjsonable_subs_id,
                self.course)

        with self.assertRaises(NotFoundError):
            contentstore().find(self.content_location_unjsonable)

    def tearDown(self):
        self.clear_subs_content()
        MongoClient().drop_database(TEST_DATA_CONTENTSTORE['DOC_STORE_CONFIG']['db'])
        _CONTENTSTORE.clear()



class TestGenerateSubsFromSource(TestDownloadYoutubeSubs):
    """Tests for `generate_subs_from_source` function."""

    def test_success_generating_subs(self):
        youtube_subs = {
            0.5: 'JMD_ifUUfsU',
            1.0: 'hI10vDNYz4M',
            2.0: 'AKqURZnYqpk'
        }
        srt_filedata = textwrap.dedent("""
            1
            00:00:10,500 --> 00:00:13,000
            Elephant's Dream

            2
            00:00:15,000 --> 00:00:18,000
            At the left we can see...
        """)
        self.clear_subs_content(youtube_subs)

        # Check transcripts_utils.TranscriptsGenerationException not thrown.
        # Also checks that uppercase file extensions are supported.
        transcripts_utils.generate_subs_from_source(youtube_subs, 'SRT', srt_filedata, self.course)

        # Check assets status after importing subtitles.
        for subs_id in youtube_subs.values():
            filename = 'subs_{0}.srt.sjson'.format(subs_id)
            content_location = StaticContent.compute_location(
                self.org, self.number, filename
            )
            self.assertTrue(contentstore().find(content_location))

        self.clear_subs_content(youtube_subs)

    def test_fail_bad_subs_type(self):
        youtube_subs = {
            0.5: 'JMD_ifUUfsU',
            1.0: 'hI10vDNYz4M',
            2.0: 'AKqURZnYqpk'
        }

        srt_filedata = textwrap.dedent("""
            1
            00:00:10,500 --> 00:00:13,000
            Elephant's Dream

            2
            00:00:15,000 --> 00:00:18,000
            At the left we can see...
        """)

        with self.assertRaises(transcripts_utils.TranscriptsGenerationException) as cm:
            transcripts_utils.generate_subs_from_source(youtube_subs, 'BAD_FORMAT', srt_filedata, self.course)
        exception_message = cm.exception.message
        self.assertEqual(exception_message, "We support only SubRip (*.srt) transcripts format.")

    def test_fail_bad_subs_filedata(self):
        youtube_subs = {
            0.5: 'JMD_ifUUfsU',
            1.0: 'hI10vDNYz4M',
            2.0: 'AKqURZnYqpk'
        }

        srt_filedata = """BAD_DATA"""

        with self.assertRaises(transcripts_utils.TranscriptsGenerationException) as cm:
            transcripts_utils.generate_subs_from_source(youtube_subs, 'srt', srt_filedata, self.course)
        exception_message = cm.exception.message
        self.assertEqual(exception_message, "Something wrong with SubRip transcripts file during parsing.")


class TestGenerateSrtFromSjson(TestDownloadYoutubeSubs):
    """Tests for `generate_srt_from_sjson` function."""

    def test_success_generating_subs(self):
        sjson_subs = {
            'start': [100, 200, 240, 390, 54000],
            'end': [200, 240, 380, 1000, 78400],
            'text': [
                'subs #1',
                'subs #2',
                'subs #3',
                'subs #4',
                'subs #5'
            ]
        }
        srt_subs = transcripts_utils.generate_srt_from_sjson(sjson_subs, 1)
        self.assertTrue(srt_subs)
        expected_subs = [
            '00:00:00,100 --> 00:00:00,200\nsubs #1',
            '00:00:00,200 --> 00:00:00,240\nsubs #2',
            '00:00:00,240 --> 00:00:00,380\nsubs #3',
            '00:00:00,390 --> 00:00:01,000\nsubs #4',
            '00:00:54,000 --> 00:01:18,400\nsubs #5',
        ]

        for sub in expected_subs:
            self.assertIn(sub, srt_subs)

    def test_success_generating_subs_speed_up(self):
        sjson_subs = {
            'start': [100, 200, 240, 390, 54000],
            'end': [200, 240, 380, 1000, 78400],
            'text': [
                'subs #1',
                'subs #2',
                'subs #3',
                'subs #4',
                'subs #5'
            ]
        }
        srt_subs = transcripts_utils.generate_srt_from_sjson(sjson_subs, 0.5)
        self.assertTrue(srt_subs)
        expected_subs = [
            '00:00:00,050 --> 00:00:00,100\nsubs #1',
            '00:00:00,100 --> 00:00:00,120\nsubs #2',
            '00:00:00,120 --> 00:00:00,190\nsubs #3',
            '00:00:00,195 --> 00:00:00,500\nsubs #4',
            '00:00:27,000 --> 00:00:39,200\nsubs #5',
        ]
        for sub in expected_subs:
            self.assertIn(sub, srt_subs)

    def test_success_generating_subs_speed_down(self):
        sjson_subs = {
            'start': [100, 200, 240, 390, 54000],
            'end': [200, 240, 380, 1000, 78400],
            'text': [
                'subs #1',
                'subs #2',
                'subs #3',
                'subs #4',
                'subs #5'
            ]
        }
        srt_subs = transcripts_utils.generate_srt_from_sjson(sjson_subs, 2)
        self.assertTrue(srt_subs)

        expected_subs = [
            '00:00:00,200 --> 00:00:00,400\nsubs #1',
            '00:00:00,400 --> 00:00:00,480\nsubs #2',
            '00:00:00,480 --> 00:00:00,760\nsubs #3',
            '00:00:00,780 --> 00:00:02,000\nsubs #4',
            '00:01:48,000 --> 00:02:36,800\nsubs #5',
        ]
        for sub in expected_subs:
            self.assertIn(sub, srt_subs)

    def test_fail_generating_subs(self):
        sjson_subs = {
            'start': [100, 200],
            'end': [100],
            'text': [
                'subs #1',
                'subs #2'
            ]
        }
        srt_subs = transcripts_utils.generate_srt_from_sjson(sjson_subs, 1)
        self.assertFalse(srt_subs)



class TestTranscript(unittest.TestCase):
    """
    Tests for Transcript class e.g. different transcript conversions.
    """
    def setUp(self):

        self.srt_transcript = textwrap.dedent("""\
            0
            00:00:10,500 --> 00:00:13,000
            Elephant&#39;s Dream

            1
            00:00:15,000 --> 00:00:18,000
            At the left we can see...

        """)


        self.sjson_transcript = textwrap.dedent("""\
            {
                "start": [
                    10500,
                    15000
                ],
                "end": [
                    13000,
                    18000
                ],
                "text": [
                    "Elephant&#39;s Dream",
                    "At the left we can see..."
                ]
            }
        """)

        self.txt_transcript = u"Elephant's Dream\nAt the left we can see..."

    def test_convert_srt_to_txt(self):
        expected = self.txt_transcript
        actual = transcripts_utils.Transcript.convert(self.srt_transcript, 'srt', 'txt')
        self.assertEqual(actual, expected)

    def test_convert_srt_to_srt(self):
        expected = self.srt_transcript
        actual = transcripts_utils.Transcript.convert(self.srt_transcript, 'srt', 'srt')
        self.assertEqual(actual, expected)

    def test_convert_sjson_to_txt(self):
        expected = self.txt_transcript
        actual = transcripts_utils.Transcript.convert(self.sjson_transcript, 'sjson', 'txt')
        self.assertEqual(actual, expected)

    def test_convert_sjson_to_srt(self):
        expected = self.srt_transcript
        actual = transcripts_utils.Transcript.convert(self.sjson_transcript, 'sjson', 'srt')
        self.assertEqual(actual, expected)

    def test_convert_srt_to_sjson(self):
        with self.assertRaises(NotImplementedError):
            transcripts_utils.Transcript.convert(self.srt_transcript, 'srt', 'sjson')


class TestSubsFilename(unittest.TestCase):
    """
    Tests for subs_filename funtion.
    """

    def test_unicode(self):
        name = transcripts_utils.subs_filename(u"˙∆©ƒƒƒ")
        self.assertEqual(name, u'subs_˙∆©ƒƒƒ.srt.sjson')
        name = transcripts_utils.subs_filename(u"˙∆©ƒƒƒ", 'uk')
        self.assertEqual(name, u'uk_subs_˙∆©ƒƒƒ.srt.sjson')
