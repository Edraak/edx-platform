from django.contrib.auth.models import User
from django.test.client import Client
from django.test.utils import override_settings

from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from student.tests.factories import (UserFactory,
                                     CourseEnrollmentFactory,
                                     UserProfileFactory)
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.django import modulestore

TEST_COURSE_ID = 'edX/Welding/Power_Welding'
DUMMY_HTML = '''<div>Welding is cool.  We weld a lot at edX,
            while putting the pieces of our site together after our
            servers blow up.</div>'''
PROBLEM_XML = '<problem>Not a real problem.</problem>'

@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class CoursewareApiTest(ModuleStoreTestCase):

    def setUp(self):
        """
        Set up a user, a course, and enroll one in the other.
        """
        self.user = UserFactory.build(username='freddy',
                                 first_name='Fred',
                                 last_name='W',
                                 email='fred@edx.org')
        self.user.set_password('test_password')
        self.user.save()


        modulestore().request_cache = None
        modulestore().metadata_inheritance_cache_subsystem = None

        # set up the course
        self.course = CourseFactory.create(display_name='Power Welding!',
                                      org='edX',
                                      number='Welding')

        # need a user profile...
        UserProfileFactory.create(user=self.user)

        chapter = ItemFactory.create(
            parent_location=self.course.location,
            template="i4x://edx/templates/sequential/Empty",
            display_name='Welcome to Welding'
        )

        section = ItemFactory.create(
            parent_location=chapter.location,
            template="i4x://edx/templates/sequential/Empty",
            display_name="Your first weld"
        )

        vertical = ItemFactory.create(
            parent_location=section.location,
            template="i4x://edx/templates/vertical/Empty",
            display_name="random hex"
        )

        video = ItemFactory.create(
            parent_location=vertical.location,
            template="i4x://edx/templates/video/default",
            display_name="See Fred Weld",
            data='<video youtube="1.0:abc123 />'
        )

        html = ItemFactory.create(
            parent_location=vertical.location,
            template="i4x://edx/templates/html/Blank_HTML_Page",
            display_name="About Welding",
            data=DUMMY_HTML
        )

        problem = ItemFactory.create(
            parent_location=vertical.location,
            template="i4x://edx/templates/problem/Blank_Common_Problem",
            display_name="About Welding",
            data=PROBLEM_XML
        )

        enrollment = CourseEnrollmentFactory.build(
            course_id=TEST_COURSE_ID,
            user=self.user)


    def test_profile(self):
        # resp = get('/profile')
        expected = {'name': 'Fred W',
                    'username': 'freddy',
                    'email': 'fred@edx.org',
                    'courses': [
                        {'course_id': TEST_COURSE_ID,
                         'name': 'Power Welding!',
                         'description': 'This is Power Welding.',
                         'image_url': 'https://www.edx.org/image.png',
                         'is_running': True}]}
        parsed = expected
        self.assertEqual(parsed, expected)



    def test_course(self):
        # Do not return stuff that isn't started

        expected = {
            'id': 'edX/Welding/2013',
            'blocks': {
                1: {'category': 'course',
                    'children': [2],
                    'metadata': {'display_name': 'Welding!'},
                    'definition': 'i4x://edX/Welding/course/2013',
                    },
                2: {'category': 'chapter',
                    'children': [3],
                    'metadata': {'display_name': 'Welcome to Welding'},
                    'definition': 'i4x://edX/Welding/chapter/Welcome_to_Welding',
                    },
                3: {'category': 'sequential',
                    'children': [4],
                    'metadata': {'display_name': 'Your first weld'},
                    'definition': 'i4x://edX/Welding/sequential/Your_first_weld',
                    },
                4: {'category': 'vertical',
                    'children': [5,6,7],
                    'metadata': {'display_name': 'random hex'},
                    'definition': 'i4x://edX/Welding/vertical/random_hex',
                    },
                5: {'category': 'video',
                    'children': [],
                    'metadata': {'display_name': 'See Fred Weld'},
                    'definition': 'i4x://edX/Welding/video/See_Fred_Weld',
                    },
                6: {'category': 'html',
                    'metadata': {'display_name': 'About Welding'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/html/About_Welding',
                    },
                7: {'category': 'problem',
'metadata': {'display_name': 'Weld this'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/problem/Weld_This',
                    }
                }
            }

        parsed = expected
        self.assertEqual(parsed, expected)



    def test_xblock_problem(self):
        expected = {
            'location': 'i4x://edX/Welding/problem/weld_this',
            'category': 'problem',
            'message': 'Problems not supported yet'
        # ???
        }
        parsed = expected
        self.assertEqual(parsed, expected)


    def test_xblock_sequential(self):
        expected = {
            'location': 'i4x://edX/Welding/sequential/your_first_weld',
            'category': 'sequential',
            'message': "Sequentials don't have any interesting definition"
        # ???
        }
        parsed = expected
        self.assertEqual(parsed, expected)

    def test_xblock_vertical(self):
        expected = {
            'location': 'i4x://edX/Welding/vertical/deadbeef',
            'category': 'vertical',
            'message': "Verticals don't have any interesting definition"
        # ???
        }
        parsed = expected
        self.assertEqual(parsed, expected)


    def test_xblock_video(self):
        expected = {
            'location': 'i4x://edX/Welding/video/see_fred_weld',
            'category': 'video',
            'youtube_id': 'abc123',
            }
        parsed = expected
        self.assertEqual(parsed, expected)


    def test_xblock_html(self):
        expected = {
            'location': 'i4x://edX/Welding/html/about_welding',
            'category': 'html',
            'html': DUMMY_HTML
            }
        parsed = expected
        self.assertEqual(parsed, expected)

