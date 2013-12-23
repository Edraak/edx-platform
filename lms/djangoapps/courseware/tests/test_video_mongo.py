# -*- coding: utf-8 -*-
"""Video xmodule tests in mongo."""

from mock import patch, PropertyMock
from . import BaseTestXmodule
from .test_video_xml import SOURCE_XML
from django.conf import settings
from xmodule.video_module import _create_youtube_string


class TestVideo(BaseTestXmodule):
    """Integration tests: web client + mongo."""

    CATEGORY = "video"
    DATA = SOURCE_XML

    def init_module(self, data=None, model_data=None, metadata=None):
        DATA = str(self.DATA)
        if data:
            self.DATA = data

        MODEL_DATA = dict(self.MODEL_DATA)
        if model_data:
            self.MODEL_DATA.update(model_data)

        METADATA = dict(self.METADATA)
        if metadata:
            self.METADATA.update(metadata)

        super(TestVideo, self).setUp()

        self.DATA = DATA
        self.MODEL_DATA = MODEL_DATA
        self.METADATA = METADATA


    def test_handle_ajax_dispatch(self):
        responses = {
            user.username: self.clients[user.username].post(
                self.get_url('whatever'),
                {},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            for user in self.users
        }

        self.assertEqual(
            set([
                response.status_code
                for _, response in responses.items()
                ]).pop(),
            404)

    def test_update_field(self):
        expected_fields = self.item_descriptor.editable_metadata_fields
        # KeyError
        self.item_descriptor.update_field('source')
        self.assertDictEqual(
            self.item_descriptor.editable_metadata_fields,
            expected_fields
        )


class TestVideoYouTube(TestVideo):
    def test_video_constructor(self):
        """Make sure that all parameters extracted correclty from xml"""
        context = self.item_module.render('student_view').content

        sources = {
            'main': u'example.mp4',
            u'mp4': u'example.mp4',
            u'webm': u'example.webm',
        }

        expected_context = {
            'data_dir': getattr(self, 'data_dir', None),
            'caption_asset_path': '/static/subs/',
            'show_captions': 'true',
            'display_name': u'A Name',
            'end': 3610.0,
            'id': self.item_module.location.html_id(),
            'sources': sources,
            'start': 3603.0,
            'sub': u'a_sub_file.srt.sjson',
            'track': '',
            'youtube_streams': _create_youtube_string(self.item_module),
            'autoplay': settings.FEATURES.get('AUTOPLAY_VIDEOS', False),
            'yt_test_timeout': 1500,
            'yt_test_url': 'https://gdata.youtube.com/feeds/api/videos/'
        }

        self.assertEqual(
            context,
            self.item_module.xmodule_runtime.render_template('video.html', expected_context)
        )


class TestVideoNonYouTube(TestVideo):
    """Integration tests: web client + mongo."""

    DATA = """
        <video show_captions="true"
        display_name="A Name"
        sub="a_sub_file.srt.sjson"
        download_video="true"
        start_time="01:00:03" end_time="01:00:10"
        >
            <source src="example.mp4"/>
            <source src="example.webm"/>
        </video>
    """
    MODEL_DATA = {
        'data': DATA
    }

    def test_video_constructor(self):
        """Make sure that if the 'youtube' attribute is omitted in XML, then
            the template generates an empty string for the YouTube streams.
        """
        sources = {
            'main': u'example.mp4',
            u'mp4': u'example.mp4',
            u'webm': u'example.webm',
        }

        context = self.item_module.render('student_view').content

        expected_context = {
            'data_dir': getattr(self, 'data_dir', None),
            'caption_asset_path': '/static/subs/',
            'show_captions': 'true',
            'display_name': u'A Name',
            'end': 3610.0,
            'id': self.item_module.location.html_id(),
            'sources': sources,
            'start': 3603.0,
            'sub': u'a_sub_file.srt.sjson',
            'track': '',
            'youtube_streams': '1.00:OEoXaMPEzfM',
            'autoplay': settings.FEATURES.get('AUTOPLAY_VIDEOS', True),
            'yt_test_timeout': 1500,
            'yt_test_url': 'https://gdata.youtube.com/feeds/api/videos/'
        }

        self.assertEqual(
            context,
            self.item_module.xmodule_runtime.render_template('video.html', expected_context)
        )

    def test_get_html_source(self):
        SOURCE_XML = """
            <video show_captions="true"
            display_name="A Name"
            sub="a_sub_file.srt.sjson" source="{source}"
            download_video="{download_video}"
            start_time="01:00:03" end_time="01:00:10"
            >
                {sources}
            </video>
        """
        cases = [
            # download_video['value'] == True
            {
                'download_video': 'true',
                'source': 'example_source.mp4',
                'sources': """
                    <source src="example.mp4"/>
                    <source src="example.webm"/>
                """,
                'result': {
                    'main': u'example_source.mp4',
                    u'mp4': u'example.mp4',
                    u'webm': u'example.webm',
                },
            },
            {
                'download_video': 'true',
                'source': '',
                'sources': """
                    <source src="example.mp4"/>
                    <source src="example.webm"/>
                """,
                'result': {
                    'main': u'example.mp4',
                    u'mp4': u'example.mp4',
                    u'webm': u'example.webm',
                },
            },
            {
                'download_video': 'true',
                'source': '',
                'sources': [],
                'result': {},
            },

            # download_video['value'] == False
            {
                'download_video': 'false',
                'source': 'example_source.mp4',
                'sources': """
                    <source src="example.mp4"/>
                    <source src="example.webm"/>
                """,
                'result': {
                    u'mp4': u'example.mp4',
                    u'webm': u'example.webm',
                },
            },
        ]

        expected_context = {
            'data_dir': getattr(self, 'data_dir', None),
            'caption_asset_path': '/static/subs/',
            'show_captions': 'true',
            'display_name': u'A Name',
            'end': 3610.0,
            'id': None,
            'sources': None,
            'start': 3603.0,
            'sub': u'a_sub_file.srt.sjson',
            'track': '',
            'youtube_streams': '1.00:OEoXaMPEzfM',
            'autoplay': settings.FEATURES.get('AUTOPLAY_VIDEOS', True),
            'yt_test_timeout': 1500,
            'yt_test_url': 'https://gdata.youtube.com/feeds/api/videos/'
        }

        for data in cases:
            DATA = SOURCE_XML.format(
                download_video=data['download_video'],
                source=data['source'],
                sources=data['sources'],
            )
            self.init_module(data=DATA)

            expected_context.update({
                'sources': data['result'],
                'id': self.item_module.location.html_id(),
            })

            context = self.item_module.render('student_view').content

            self.assertEqual(
                context,
                self.item_module.xmodule_runtime.render_template('video.html', expected_context)
            )


class VideoBackwardsCompatibilityTestCase(TestVideo):
    """
    Make sure that Backwards Compatibility works correctly.
    """
    def test_source_not_in_html5sources(self):
        field_data = {
            'source': 'http://example.org/video.mp4',
            'html5_sources': ['http://youtu.be/OEoXaMPEzfM.mp4'],
        }

        self.init_module(metadata=field_data)

        fields = self.item_descriptor.editable_metadata_fields

        expected = {
            'source': 'http://example.org/video.mp4',
            'download_video': True,
        }

        self.assertDictEqual({
            'source': fields['source']['value'],
            'download_video': fields['download_video']['value'],
        }, expected)
        self.assertTrue(fields['download_video']['explicitly_set'])
        self.assertTrue(fields['source']['non_editable'])

    def test_source_in_html5sources(self):
        field_data = {
            'source': 'http://example.org/video.mp4',
            'html5_sources': ['http://example.org/video.mp4'],
        }

        self.init_module(metadata=field_data)

        fields = self.item_descriptor.editable_metadata_fields

        self.assertNotIn('source', fields)
        self.assertTrue(fields['download_video']['value'])

    @patch('xmodule.x_module.XModuleDescriptor.editable_metadata_fields', new_callable=PropertyMock)
    def test_download_video_is_explicitly_set(self, mock_editable_fields):
        mock_editable_fields.return_value = {
            'download_video': {
                'default_value': False,
                'explicitly_set': True,
                'display_name': 'Allow to Download Video',
                'help': 'Allow to download the video.',
                'type': 'Boolean',
                'value': False,
                'field_name': 'download_video',
                'options': [
                    {'display_name': "True", "value": True},
                    {'display_name': "False", "value": False}
                ]
            },
            'html5_sources': {
                'default_value': [],
                'explicitly_set': False,
                'display_name': 'Video Sources',
                'help': 'A list of filenames to be used with HTML5 video.',
                'type': 'List',
                'value': [u'http://youtu.be/OEoXaMPEzfM.mp4'],
                'field_name': 'html5_sources',
                'options': []
            },
            'source': {
                'default_value': '',
                'explicitly_set': False,
                'display_name': 'Download Video',
                'help': 'The external URL to download the video.',
                'type': 'Generic',
                'value': u'http://example.org/video.mp4',
                'field_name': 'source',
                'options': []
            },
        }

        self.item_descriptor.editable_metadata_fields

        fields = self.item_descriptor.editable_metadata_fields

        self.assertTrue(fields['download_video']['explicitly_set'])
        self.assertTrue(fields['source']['non_editable'])
        self.assertFalse(fields['download_video']['value'])

    def test_source_is_empty(self):
        field_data = {
            'source': '',
            'html5_sources': ['http://youtu.be/OEoXaMPEzfM.mp4'],
        }

        self.init_module(metadata=field_data)

        fields = self.item_descriptor.editable_metadata_fields

        self.assertNotIn('source', fields)
        self.assertFalse(fields['download_video']['value'])

