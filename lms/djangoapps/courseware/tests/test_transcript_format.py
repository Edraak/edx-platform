# -*- coding: utf-8 -*-
"""
Test for transcript Srt class
"""
import unittest
import textwrap
import json
from mock import patch


from xmodule.video_module import srt, sjson
from xmodule.video_module.transcript import Transcript


class TestSrt(unittest.TestCase):
    """
    Verify that loading and converstion from srt to diferent formats works OK.
    """
    def setUp(self):
        super(TestSrt, self).setUp()
        self.content = textwrap.dedent("""
            0
            00:00:00,012 --> 00:00:00,100
            Привіт, edX вітає вас.
        """)

    def test_convert_to_sjson(self):
        sjson = srt.convert_to_sjson(self.content)
        self.assertEqual(
            json.loads(sjson),
            {
                "start": [12],
                "end": [100],
                "text": [u'Привіт, edX вітає вас.']
            }
        )

    def test_convert_to_txt(self):
        txt = srt.convert_to_txt(self.content)
        self.assertEqual(txt, u'Привіт, edX вітає вас.')



class TestSjson(unittest.TestCase):
    """
    Verify that loading and converstion from sjson to diferent formats works OK.
    """
    def setUp(self):
        super(TestSjson, self).setUp()
        self.content = json.dumps({
            "start": [12],
            "end": [100],
            "text": [u'Привіт, edX вітає вас.']
        })

    def test_convert_to_srt(self):
        srt = sjson.convert_to_srt(self.content)
        correct = textwrap.dedent(u"""
            0
            00:00:00,012 --> 00:00:00,100
            Привіт, edX вітає вас.

        """).lstrip('\n')
        self.assertEqual(srt, correct)

    def test_convert_to_txt(self):
        txt = sjson.convert_to_txt(self.content)
        self.assertEqual(txt, u'Привіт, edX вітає вас.')


class TestTranscript(unittest.TestCase):
    """
    Verify that `convert` calls to right methods
    """

    def test_convert(self):
        """
        Test that proper convertion methods are called
        """

        with patch('xmodule.video_module.sjson.convert_to_srt') as mock:
            Transcript.convert('sjson', 'srt')('Some data', 'some_translation_function')
            mock.assert_called_with('Some data', 'some_translation_function')

        with patch('xmodule.video_module.sjson.convert_to_txt') as mock:
            Transcript.convert('sjson', 'txt')('Some data', 'some_translation_function')
            mock.assert_called_with('Some data', 'some_translation_function')

        with patch('xmodule.video_module.srt.convert_to_txt') as mock:
            Transcript.convert('srt', 'txt')('Some data', 'some_translation_function')
            mock.assert_called_with('Some data', 'some_translation_function')

        with patch('xmodule.video_module.srt.convert_to_sjson') as mock:
            Transcript.convert('srt', 'sjson')('Some data', 'some_translation_function')
            mock.assert_called_with('Some data', 'some_translation_function')

        self.assertEqual(
            Transcript.convert('srt', 'unknown')('Some data', 'some_translation_function'),
            'Some data'
        )
        self.assertEqual(
            Transcript.convert('unknown', 'srt')('Some data', 'some_translation_function'),
            'Some data'
        )

