"""
Test video utils.
"""
import unittest
from xmodule.video_module import video_utils


class TestVideoUtils(unittest.TestCase):

    def test_subs_for_html5_vid_with_periods(self):
        """
        This is to verify a fix whereby subtitle files uploaded against
        a HTML5 video that contains periods in the name causes
        incorrect subs name parsing
        """
        html5_ids = video_utils.get_html5_ids(['foo.mp4', 'foo.1.bar.mp4', 'foo/bar/baz.1.4.mp4', 'foo'])
        self.assertEqual(4, len(html5_ids))
        self.assertEqual(html5_ids[0], 'foo')
        self.assertEqual(html5_ids[1], 'foo.1.bar')
        self.assertEqual(html5_ids[2], 'baz.1.4')
        self.assertEqual(html5_ids[3], 'foo')
