import calendar
import copy
import time
from uuid import uuid4

from django.test import TestCase

from django.conf import settings
import xmodule.modulestore.django
from xmodule.templates import update_templates


from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import FakePayload, Client
from django.test.utils import override_settings

from tastypie.serializers import Serializer
from tastypie.test import TestApiClient, ResourceTestCase

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


class ModuleResourceTestCase(ResourceTestCase):
    """
    Until we find a better way, copy+paste the MongoStoreTestCase class here, but
    inherit from the tastypie ResourceTestCase.

    @all: is there a better way to do this?

    Subclass for any test case that uses the mongodb
    module store. This populates a uniquely named modulestore
    collection with templates before running the TestCase
    and drops it they are finished. """

    @staticmethod
    def flush_mongo_except_templates():
        '''
        Delete everything in the module store except templates
        '''
        modulestore = xmodule.modulestore.django.modulestore()

        # This query means: every item in the collection
        # that is not a template
        query = {"_id.course": {"$ne": "templates"}}

        # Remove everything except templates
        modulestore.collection.remove(query)

    @staticmethod
    def load_templates_if_necessary():
        '''
        Load templates into the modulestore only if they do not already exist.
        We need the templates, because they are copied to create
        XModules such as sections and problems
        '''
        modulestore = xmodule.modulestore.django.modulestore()

        # Count the number of templates
        query = {"_id.course": "templates"}
        num_templates = modulestore.collection.find(query).count()

        if num_templates < 1:
            update_templates()

    @classmethod
    def setUpClass(cls):
        '''
        Flush the mongo store and set up templates
        '''

        # Use a uuid to differentiate
        # the mongo collections on jenkins.
        cls.orig_modulestore = copy.deepcopy(settings.MODULESTORE)
        if 'direct' not in settings.MODULESTORE:
            settings.MODULESTORE['direct'] = settings.MODULESTORE['default']

        settings.MODULESTORE['default']['OPTIONS']['collection'] = 'modulestore_%s' % uuid4().hex
        settings.MODULESTORE['direct']['OPTIONS']['collection'] = 'modulestore_%s' % uuid4().hex
        xmodule.modulestore.django._MODULESTORES.clear()

        print settings.MODULESTORE

        TestCase.setUpClass()

    @classmethod
    def tearDownClass(cls):
        '''
        Revert to the old modulestore settings
        '''

        # Clean up by dropping the collection
        modulestore = xmodule.modulestore.django.modulestore()
        modulestore.collection.drop()

        xmodule.modulestore.django._MODULESTORES.clear()

        # Restore the original modulestore settings
        settings.MODULESTORE = cls.orig_modulestore

    def _pre_setup(self):
        '''
        Remove everything but the templates before each test
        '''

        # Flush anything that is not a template
        ModuleResourceTestCase.flush_mongo_except_templates()

        # Check that we have templates loaded; if not, load them
        ModuleResourceTestCase.load_templates_if_necessary()

        # Call superclass implementation
        super(ModuleResourceTestCase, self)._pre_setup()

    def _post_teardown(self):
        '''
        Flush everything we created except the templates
        '''
        # Flush anything that is not a template
        ModuleResourceTestCase.flush_mongo_except_templates()

        # Call superclass implementation
        super(ModuleResourceTestCase, self)._post_teardown()



@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class CoursewareApiTest(ModuleResourceTestCase):

    def setUp(self):
        """
        Set up a user, a course, and enroll one in the other.
        """
        super(CoursewareApiTest, self).setUp()

        self.maxDiff = None

        self.user = UserFactory.build(username='freddy',
                                 first_name='Fred',
                                 last_name='W',
                                 email='fred@edx.org')
        self.user.set_password('test_password')
        self.user.save()

        # need a user profile...
        UserProfileFactory.create(user=self.user)

        modulestore().request_cache = None
        modulestore().metadata_inheritance_cache_subsystem = None

        # set up the course
        earlier = time.gmtime(time.time() - 3600*24)
        self.course = CourseFactory.create(display_name='Power Welding',
                                      org='edX',
                                      number='Welding',
                                      start=earlier)

        chapter = ItemFactory.create(
            parent_location=self.course.location,
            template="i4x://edx/templates/chapter/Empty",
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
            display_name="Weld This",
            data=PROBLEM_XML
        )

        enrollment = CourseEnrollmentFactory.build(
            course_id=TEST_COURSE_ID,
            user=self.user)
        enrollment.save()


    def test_profile(self):
        url = reverse('api_dispatch_detail',
                      kwargs={'resource_name': 'profile',
                              'pk': 'freddy'})
        resp = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(resp)

        expected = {'name': 'Fred W',
                    'username': 'freddy',
                    'email': 'fred@edx.org',
                    'courses': [
                        {'course_id': TEST_COURSE_ID,
                         'name': 'Power Welding',
                         'description': '',
                         'image_url': '/c4x/edX/Welding/asset/images_course_image.jpg',
                         'is_running': True}]}
        parsed = self.deserialize(resp)
        self.assertEqual(parsed, expected)



    def test_course(self):
        # TODO: Test that we do not return elements that haven't isn't started

        url = reverse('api_dispatch_detail',
                      kwargs={'resource_name': 'course',
                              'pk': TEST_COURSE_ID})

        resp = self.api_client.get(url, format='json')
        self.assertValidJSONResponse(resp)

        expected = {
            'id': 'edX/Welding/Power_Welding',
            'blocks': {
                'i4x://edX/Welding/course/Power_Welding': {'category': 'course',
                    'children': ['i4x://edX/Welding/chapter/Welcome_to_Welding'],
                    'metadata': {'display_name': 'Power Welding'},
                    'definition': 'i4x://edX/Welding/course/Power_Welding',
                    },
                'i4x://edX/Welding/chapter/Welcome_to_Welding': {'category': 'chapter',
                    'children': ['i4x://edX/Welding/sequential/Your_first_weld'],
                    'metadata': {'display_name': 'Welcome to Welding'},
                    'definition': 'i4x://edX/Welding/chapter/Welcome_to_Welding',
                    },
                'i4x://edX/Welding/sequential/Your_first_weld': {'category': 'sequential',
                    'children': ['i4x://edX/Welding/vertical/random_hex'],
                    'metadata': {'display_name': 'Your first weld'},
                    'definition': 'i4x://edX/Welding/sequential/Your_first_weld',
                    },
                'i4x://edX/Welding/vertical/random_hex': {'category': 'vertical',
                    'children': ['i4x://edX/Welding/video/See_Fred_Weld',
                                 'i4x://edX/Welding/html/About_Welding',
                                 'i4x://edX/Welding/problem/Weld_This'],
                    'metadata': {'display_name': 'random hex'},
                    'definition': 'i4x://edX/Welding/vertical/random_hex',
                    },
                'i4x://edX/Welding/video/See_Fred_Weld': {'category': 'video',
                    'children': [],
                    'metadata': {'display_name': 'See Fred Weld'},
                    'definition': 'i4x://edX/Welding/video/See_Fred_Weld',
                    },
                'i4x://edX/Welding/html/About_Welding': {'category': 'html',
                    'metadata': {'display_name': 'About Welding'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/html/About_Welding',
                    },
                'i4x://edX/Welding/problem/Weld_This': {'category': 'problem',
'metadata': {'display_name': 'Weld This'},
                    'children': [],
                    'definition': 'i4x://edX/Welding/problem/Weld_This',
                    }
                }
            }

        parsed = self.deserialize(resp)
        # First, let's make sure the keys match
        self.assertKeys(parsed, expected)

        # now make sure everything matches

        self.assertEqual(parsed, expected)



    def test_xblock_problem(self):
        # TODO: correct error status code instead of 'error message'
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

