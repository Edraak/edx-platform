# -*- coding: utf-8 -*-
"""Test for Video Alpha Xmodule functional logic.
These tests data readed from  xml, not from mongo.

we have a ModuleStoreTestCase class defined in common/lib/xmodule/xmodule/modulestore/tests/django_utils.py. You can search for usages of this in the cms and lms tests for examples. You use this so that it will do things like point the modulestore setting to mongo, flush the contentstore before and after, load the templates, etc.
You can then use the CourseFactory and XModuleItemFactory as defined in common/lib/xmodule/xmodule/modulestore/tests/factories.py to create the course, section, subsection, unit, etc.
"""

from mock import Mock
from lxml import etree

from xmodule.video_module import VideoDescriptor, VideoModule
from xmodule.modulestore import Location

from . import test_system
from .test_logic import LogicTest


class VideoFactory(object):

    """
    A helper class to create video modules with various parameters for testing.
    """

    # tag that uses youtube videos
    sample_problem_xml_youtube = """
        <video show_captions="true"
        youtube="0.75:jNCf2gIqpeE,1.0:ZwkTiUPN0mg,1.25:rsq9auxASqI,1.50:kMyNdzVHHgg"
        data_dir=""
        caption_asset_path=""
        autoplay="true"
        from="01:00:03" to="01:00:10"
        >
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.mp4"/>
        </video>
    """

    @staticmethod
    def create():
        """
        All parameters are optional, and are added to the created problem if specified.

        Arguments:
            TODO: describe
        """
        location = Location(["i4x", "edX", "video", "default",
                             "SampleProblem{0}".format(1)])
        model_data = {'data': VideoFactory.sample_problem_xml_youtube}

        descriptor = Mock(weight="1")

        system = test_system()
        module = VideoModule(system, location, descriptor, model_data)

        return module


class VideoModuleTest(LogicTest):
    descriptor_class = VideoDescriptor

    raw_model_data = {
        'data': '<video />'
    }

    def test_get_timeframe_no_parameters(self):
        """Make sure that timeframe() works correctly w/o parameters"""
        xmltree = etree.fromstring('<video>test</video>')
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, ('', ''))

    def test_get_timeframe_with_one_parameter(self):
        """Make sure that timeframe() works correctly with one parameter"""
        xmltree = etree.fromstring(
            '<video from="00:04:07">test</video>'
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, ''))

    def test_get_timeframe_with_two_parameters(self):
        """Make sure that timeframe() works correctly with two parameters"""
        xmltree = etree.fromstring(
            '''<video
                    from="00:04:07"
                    to="13:04:39"
                >test</video>'''
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, 47079))

    def test_video_constructor(self):
        """Make sure that all parameters extracted correclty from xml"""
        module = VideoFactory.create()
