# -*- coding: utf-8 -*-
"""Test for Video Alpha Xmodule functional logic.
These tests data readed from  xml, not from mongo.

we have a ModuleStoreTestCase class defined in common/lib/xmodule/xmodule/modulestore/tests/django_utils.py. You can search for usages of this in the cms and lms tests for examples. You use this so that it will do things like point the modulestore setting to mongo, flush the contentstore before and after, load the templates, etc.
You can then use the CourseFactory and XModuleItemFactory as defined in common/lib/xmodule/xmodule/modulestore/tests/factories.py to create the course, section, subsection, unit, etc.





"""

from xmodule.videoalpha_module import VideoAlphaDescriptor, VideoAlphaModule
from . import PostData, LogicTest, etree
from xmodule.modulestore import Location
from mock import Mock
from . import test_system

class VideoAlphaFactory(object):

    """
    A helper class to create videoalpha modules with various parameters for testing.
    """

    # tag that uses youtube videos
    sample_problem_xml_youtube = """
        <videoalpha show_captions="true"
        youtube="0.75:jNCf2gIqpeE,1.0:ZwkTiUPN0mg,1.25:rsq9auxASqI,1.50:kMyNdzVHHgg"
        data_dir=""
        show_captions="true"
        caption_asset_path=""
        autoplay="true"
        from="01:00:03" to="01:00:10"
        >
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.mp4"/>
        </videoalpha>
    """
    # tag that uses html5 video
    sample_problem_xml_html5 = """
        <videoalpha show_captions="true"
        youtube=""
        sub="jNCf2gIqpeE12345"
        from="01:00:03" to="01:00:10"
        show_captions="true"
        caption_asset_path=""
        autoplay="true"
        >
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.mp4"/>
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.webm"/>
            <source src=".../mit-3091x/M-3091X-FA12-L21-3_100.ogv"/>

        </videoalpha>
    """

    sample_problem_xml = """<videoalpha> </videoalpha>
    """

    @staticmethod
    def create(youtube=None,
               sub=None,
               autoplay=None,
               show_captions=None,
               data_dir=None,
               caption_asset_path=None,
               time_from=None,
               time_to=None,
               ):
        """
        All parameters are optional, and are added to the created problem if specified.

        Arguments:
            TODO: describe
        """
        location = Location(["i4x", "edX", "videoalpha_test", "videoalpha",
                             "SampleProblem{0}".format(1)])
        model_data = {'data': VideoAlphaFactory.sample_problem_xml}

        if youtube is not None:
            model_data['youtube'] = youtube
        if sub is not None:
            model_data['sub'] = sub
        if autoplay is not None:
            model_data['autoplay'] = autoplay
        if show_captions is not None:
            model_data['show_captions'] = show_captions
        if data_dir is not None:
            model_data['data_dir'] = data_dir
        if caption_asset_path is not None:
            model_data['caption_asset_path'] = caption_asset_path
        if time_from is not None:
            model_data['from'] = time_from
        if time_to is not None:
            model_data['to'] = time_to

        descriptor = Mock(weight="1")

        system = test_system()
        system.render_template = Mock(return_value="<div>Test Template HTML</div>")
        module = VideoAlphaModule(system, location, descriptor, model_data)

        return module

class VideoAlphaModuleTest(LogicTest):
    descriptor_class = VideoAlphaDescriptor

    raw_model_data = {
        'data': '<videoalpha />'
    }




    def test_get_timeframe_no_parameters(self):
        "Make sure that timeframe() works correctly w/o parameters"
        xmltree = etree.fromstring('<videoalpha>test</videoalpha>')
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, ('', ''))

    def test_get_timeframe_with_one_parameter(self):
        "Make sure that timeframe() works correctly with one parameter"
        xmltree = etree.fromstring(
            '<videoalpha start_time="00:04:07">test</videoalpha>'
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, ''))

    def test_get_timeframe_with_two_parameters(self):
        "Make sure that timeframe() works correctly with two parameters"
        xmltree = etree.fromstring(
            '''<videoalpha
                    start_time="00:04:07"
                    end_time="13:04:39"
                >test</videoalpha>'''
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, 47079))

    def test_video_constructor(self):
        "Make sure that all parameters extracted correclty from xml"
        # output = self.xmodule
        module = VideoAlphaFactory.create()
        import ipdb; ipdb.set_trace()


#
