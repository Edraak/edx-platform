"""
This test file will run through some XBlock test scenarios regarding the
recommender system
"""
import json
import itertools
import StringIO
from ddt import ddt, data
from copy import deepcopy

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from courseware.tests.helpers import LoginEnrollmentTestCase
from courseware.tests.modulestore_config import TEST_DATA_MIXED_MODULESTORE
from courseware.tests.factories import GlobalStaffFactory

from lms.lib.xblock.runtime import quote_slashes


@override_settings(MODULESTORE=TEST_DATA_MIXED_MODULESTORE)
class TestRecommender(ModuleStoreTestCase, LoginEnrollmentTestCase):
    """
    Check that Recommender state is saved properly.
    """
    STUDENT_INFO = [('view@test.com', 'foo'), ('view2@test.com', 'foo')]

    def setUp(self):
        self.course = CourseFactory.create(
            display_name='Recommender_Test_Course'
        )
        self.chapter = ItemFactory.create(
            parent=self.course, display_name='Overview'
        )
        self.section = ItemFactory.create(
            parent=self.chapter, display_name='Welcome'
        )
        self.unit = ItemFactory.create(
            parent=self.section, display_name='New Unit'
        )
        self.xblock = ItemFactory.create(
            parent=self.unit,
            category='recommender',
            display_name='recommender'
        )
        self.xblock2 = ItemFactory.create(
            parent=self.unit,
            category='recommender',
            display_name='recommender_second'
        )

        self.xblock_names = ['recommender', 'recommender_second']

        self.course_url = reverse(
            'courseware_section',
            kwargs={
                'course_id': self.course.id.to_deprecated_string(),
                'chapter': 'Overview',
                'section': 'Welcome',
            }
        )
        
        self.test_recommendations = [
            {
                "title": "Covalent bonding and periodic trends",
                "url": (
                    "https://courses.edx.org/courses/MITx/3.091X/"
                    "2013_Fall/courseware/SP13_Week_4/"
                    "SP13_Periodic_Trends_and_Bonding/"
                ),
                "description": (
                    "http://people.csail.mit.edu/swli/edx/"
                    "recommendation/img/videopage1.png"
                ),
                "descriptionText": (
                    "short description for Covalent bonding "
                    "and periodic trends"
                )
            },
            {
                "title": "Polar covalent bonds and electronegativity",
                "url": (
                    "https://courses.edx.org/courses/MITx/3.091X/"
                    "2013_Fall/courseware/SP13_Week_4/SP13_Covalent_Bonding/"
                ),
                "description": (
                    "http://people.csail.mit.edu/swli/edx/"
                    "recommendation/img/videopage2.png"
                ),
                "descriptionText": (
                    "short description for Polar covalent "
                    "bonds and electronegativity"
                )
            }
        ]

        # Create student accounts and activate them.
        for i, (email, password) in enumerate(self.STUDENT_INFO):
            username = "u{}".format(i)
            self.create_account(username, email, password)
            self.activate_user(email)

        self.staff_user = GlobalStaffFactory()

    def get_handler_url(self, handler, xblock_name='recommender'):
        """
        Get url for the specified xblock handler
        """
        return reverse('xblock_handler', kwargs={
            'course_id': self.course.id.to_deprecated_string(),
            'usage_id': quote_slashes(self.course.id.make_usage_key('recommender', xblock_name).to_deprecated_string()),
            'handler': handler,
            'suffix': ''
        })

    def enroll_student(self, email, password):
        """
        Student login and enroll for the course
        """
        self.login(email, password)
        self.enroll(self.course, verify=True)

    def enroll_staff(self, staff):
        """
        Staff login and enroll for the course
        """
        email = staff.email
        password = 'test'
        self.login(email, password)
        self.enroll(self.course, verify=True)

    def add_resource(self, resource, xblock_name='recommender'):
        """
        Add resource to RecommenderXBlock
        """
        url = self.get_handler_url('add_resource', xblock_name)
        resp = self.client.post(url, json.dumps(resource), '')
        return json.loads(resp.content)

    def initialize_database_by_id(
        self, handler, resource_id, times, xblock_name='recommender'
    ):
        """
        Call a ajax event (vote, delete, endorse) on a resource by its id
        several times
        """
        url = self.get_handler_url(handler, xblock_name)
        for _ in range(0, times):
            self.client.post(url, json.dumps({'id': resource_id}), '')

    def call_event(self, handler, event_data, xblock_name='recommender'):
        """
        Call a ajax event (edit, flag) on a resource by providing data
        """
        url = self.get_handler_url(handler, xblock_name)
        resp = self.client.post(url, json.dumps(event_data), '')
        return json.loads(resp.content)


class TestRecommenderCreateFromEmpty(TestRecommender):
    """
    Check whether we can add resources to an empty database correctly
    """
    def test_add_resource(self):
        """
        Verify the addition of new resource is handled correctly
        """
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        # Check whether adding new resource is successful
        for index, resource in enumerate(self.test_recommendations):
            for xblock_name in self.xblock_names:
                result = self.add_resource(resource, xblock_name)

                expected_result = {
                    'Success': True,
                    'upvotes': 0,
                    'downvotes': 0,
                    'id': index
                }
                for field in resource:
                    expected_result[field] = resource[field]

                self.assertDictEqual(result, expected_result)
                self.assert_request_status_code(200, self.course_url)


class TestRecommenderWithResources(TestRecommender):
    """
    Check whether we can add/edit/delete resources, or evaluate a resource by
    voting/endorsing/flagging correctly
    """
    def setUp(self):
        # call the setUp function from the superclass
        super(TestRecommenderWithResources, self).setUp()
        self.set_up_resources()

    def set_up_resources(self):
        """
        Set up resources and enroll staff
        """
        self.logout()
        self.enroll_staff(self.staff_user)
        # Add resources, assume correct here, tested in test_add_resource
        for resource, xblock_name in itertools.product(
            self.test_recommendations, self.xblock_names
        ):
            self.add_resource(resource, xblock_name)

    def generate_edit_resource(self, resource_id):
        """
        Generate the resource for edit
        """
        event_data = {"id": resource_id}
        edited_recommendations = {key: value + " edited" for key, value in self.test_recommendations[0].iteritems()}
        event_data.update(edited_recommendations)
        return event_data

    def test_add_redundant_resource(self):
        """
        Verify the addition of a redundant resource (url) is rejected
        """
        for suffix in ['', '#IAmSuffix', '%23IAmSuffix']:
            resource = deepcopy(self.test_recommendations[0])
            resource['url'] += suffix
            result = self.add_resource(resource)

            expected_result = {
                'Success': False,
                'error': 'redundant resource',
                'dup_id': 0
            }
            for field in resource:
                expected_result[field] = resource[field]
                expected_result['dup_' + field] = self.test_recommendations[0][field]

            self.assertDictEqual(result, expected_result)
            self.assert_request_status_code(200, self.course_url)

    def test_delete_resource_non_existing(self):
        """
        Delete a non-existing resource
        """
        resp = self.call_event('delete_resource', {'id': 100})
        self.assertEqual(resp['error'], 'bad id')
        self.assert_request_status_code(200, self.course_url)

    def test_delete_resource_once(self):
        """
        Delete a resource
        """
        resp = self.call_event('delete_resource', {'id': 1})
        self.assertEqual(resp['Success'], True)
        self.assert_request_status_code(200, self.course_url)

    def test_delete_resource_twice(self):
        """
        Delete a resource twice
        """
        self.initialize_database_by_id('delete_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event('delete_resource', {'id': 1})
        self.assertEqual(resp['error'], 'bad id')
        self.assert_request_status_code(200, self.course_url)

    def test_delete_different_resources(self):
        """
        Delete two different resources
        """
        self.initialize_database_by_id('delete_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event('delete_resource', {'id': 0})
        self.assertEqual(resp['Success'], True)
        self.assert_request_status_code(200, self.course_url)

    def test_delete_resources_in_different_xblocks(self):
        """
        Delete two resources in two different xblocks
        """
        self.initialize_database_by_id('delete_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event(
            'delete_resource',
            {'id': 1},
            xblock_name=self.xblock_names[1]
        )
        self.assertEqual(resp['Success'], True)
        self.assert_request_status_code(200, self.course_url)

    def test_delete_resource_by_student(self):
        """
        Delete resource by student
        """
        self.logout()
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        # Test
        resp = self.call_event('delete_resource', {'id': 1})
        self.assertEqual(resp['error'], 'Delete resource without permission')
        self.assert_request_status_code(200, self.course_url)

    def test_edit_resource_non_existing(self):
        """
        Edit a non-existing resource
        """
        resp = self.call_event(
            'edit_resource', self.generate_edit_resource(100)
        )
        self.assertEqual(resp['error'], 'bad id')
        self.assert_request_status_code(200, self.course_url)

    def test_edit_redundant_resource(self):
        """
        Check whether changing the url to the one of 'another' resource is
        rejected
        """
        for suffix in ['', '#IAmSuffix', '%23IAmSuffix']:
            event_data = self.generate_edit_resource(0)
            event_data['url'] = self.test_recommendations[1]['url'] + suffix
            resp = self.call_event('edit_resource', event_data)
            self.assertEqual(resp['error'], 'existing url')
            self.assertEqual(resp['dup_id'], 1)
            self.assert_request_status_code(200, self.course_url)

    def test_edit_resource(self):
        """
        Check whether changing the content of resource is successful
        """
        resp = self.call_event(
            'edit_resource', self.generate_edit_resource(0)
        )
        self.assertEqual(resp['Success'], True)
        self.assert_request_status_code(200, self.course_url)

    def test_edit_resources_in_different_xblocks(self):
        """
        Check whether changing the content of resource is successful in two
        different xblocks
        """
        event_data = self.generate_edit_resource(0)
        for xblock_name in self.xblock_names:
            resp = self.call_event('edit_resource', event_data, xblock_name)
            self.assertEqual(resp['Success'], True)
            self.assert_request_status_code(200, self.course_url)

    def test_endorse_resource_non_existing(self):
        """
        Endorse a non-existing resource
        """
        resp = self.call_event('endorse_resource', {'id': 100})
        self.assertEqual(resp['error'], 'bad id')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_resource_once(self):
        """
        Endorse a resource
        """
        resp = self.call_event('endorse_resource', {'id': 1})
        self.assertEqual(resp['status'], 'endorsement')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_resource_twice(self):
        """
        Endorse and then un-endorse a resource
        """
        self.initialize_database_by_id('endorse_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event('endorse_resource', {'id': 1})
        self.assertEqual(resp['status'], 'undo endorsement')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_resource_thrice(self):
        """
        Endorse and then un-endorse a resource
        """
        self.initialize_database_by_id('endorse_resource', resource_id=1, times=2)
        # Test
        resp = self.call_event('endorse_resource', {'id': 1})
        self.assertEqual(resp['status'], 'endorsement')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_different_resources(self):
        """
        Endorse two different resources
        """
        self.initialize_database_by_id('endorse_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event('endorse_resource', {'id': 0})
        self.assertEqual(resp['status'], 'endorsement')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_resources_in_different_xblocks(self):
        """
        Endorse two resources in two different xblocks
        """
        self.initialize_database_by_id('endorse_resource', resource_id=1, times=1)
        # Test
        resp = self.call_event(
            'endorse_resource',
            {'id': 1},
            xblock_name=self.xblock_names[1]
        )
        self.assertEqual(resp['status'], 'endorsement')
        self.assert_request_status_code(200, self.course_url)

    def test_endorse_resource_by_student(self):
        """
        Endorse resource by student
        """
        self.logout()
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        # Test
        resp = self.call_event('endorse_resource', {'id': 1})
        self.assertEqual(resp['error'], 'Endorse resource without permission')
        self.assert_request_status_code(200, self.course_url)

    def test_vote_resource_non_existing(self):
        """
        Vote a non-existing resource
        """
        for handler in ['handle_upvote', 'handle_downvote']:
            resp = self.call_event(handler, {'id': 100})
            self.assertEqual(resp['error'], 'bad id')
            self.assert_request_status_code(200, self.course_url)

    def test_vote_resource_once(self):
        """
        Vote a resource
        """
        for handler, r_id, votes in zip(
            ['handle_upvote', 'handle_downvote'], [0, 1], [1, -1]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_vote_resource_twice(self):
        """
        Vote a resource twice
        """
        for handler, r_id in zip(['handle_upvote', 'handle_downvote'], [0, 1]):
            self.initialize_database_by_id(handler, resource_id=r_id, times=1)
        # Test
        for handler, r_id, votes in zip(
            ['handle_upvote', 'handle_downvote'], [0, 1], [0, 0]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_vote_resource_thrice(self):
        """
        Vote a resource thrice
        """
        for handler, r_id in zip(['handle_upvote', 'handle_downvote'], [0, 1]):
            self.initialize_database_by_id(handler, resource_id=r_id, times=2)
        # Test
        for handler, r_id, votes in zip(
            ['handle_upvote', 'handle_downvote'], [0, 1], [1, -1]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_switch_vote_resource(self):
        """
        Switch the vote of a resource
        """
        for handler, r_id in zip(['handle_upvote', 'handle_downvote'], [0, 1]):
            self.initialize_database_by_id(handler, resource_id=r_id, times=1)
        # Test
        for handler, r_id, votes in zip(
            ['handle_downvote', 'handle_upvote'], [0, 1], [-1, 1]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_vote_different_resources(self):
        """
        Vote two different resources
        """
        for handler, r_id, votes in zip(
            [
                'handle_upvote',
                'handle_upvote',
                'handle_downvote',
                'handle_downvote'
            ],
            [0, 1, 0, 1],
            [1, 1, -1, -1]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_vote_resources_in_different_xblocks(self):
        """
        Vote two resources in two different xblocks
        """
        for handler, r_id in zip(['handle_upvote', 'handle_downvote'], [0, 1]):
            self.initialize_database_by_id(handler, resource_id=r_id, times=1)
        # Test
        for handler, r_id, votes in zip(
            ['handle_upvote', 'handle_downvote'], [0, 1], [1, -1]
        ):
            resp = self.call_event(
                handler,
                {'id': r_id},
                xblock_name=self.xblock_names[1]
            )
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_vote_resource_by_different_users(self):
        """
        Vote resource by two different users
        """
        for handler, r_id in zip(['handle_upvote', 'handle_downvote'], [0, 1]):
            self.initialize_database_by_id(handler, resource_id=r_id, times=1)
        self.logout()
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        # Test
        for handler, r_id, votes in zip(
            ['handle_upvote', 'handle_downvote'], [0, 1], [2, -2]
        ):
            resp = self.call_event(handler, {'id': r_id})
            self.assertEqual(resp['newVotes'], votes)
            self.assert_request_status_code(200, self.course_url)

    def test_flag_resource_wo_reason(self):
        """
        Flag a resource as problematic, without providing the reason
        """
        event_data = {'id': 0, 'isProblematic': True, 'reason': ''}
        # Test
        resp = self.call_event('flag_resource', event_data)
        self.assertEqual(resp['Success'], True)
        self.assertEqual(resp['reason'], '')
        self.assert_request_status_code(200, self.course_url)

    def test_flag_resource_w_reason(self):
        """
        Flag a resource as problematic, with providing the reason
        """
        event_data = {'id': 0, 'isProblematic': True, 'reason': 'reason 0'}
        # Test
        resp = self.call_event('flag_resource', event_data)
        self.assertEqual(resp['Success'], True)
        self.assertEqual(resp['reason'], 'reason 0')
        self.assert_request_status_code(200, self.course_url)

    def test_flag_resource_change_reason(self):
        """
        Flag a resource as problematic twice, with different reasons
        """
        event_data = {'id': 0, 'isProblematic': True, 'reason': 'reason 0'}
        resp = self.call_event('flag_resource', event_data)
        # Test
        event_data = {'id': 0, 'isProblematic': True, 'reason': 'reason 1'}
        resp = self.call_event('flag_resource', event_data)
        self.assertEqual(resp['Success'], True)
        self.assertEqual(resp['oldReason'], 'reason 0')
        self.assertEqual(resp['reason'], 'reason 1')
        self.assert_request_status_code(200, self.course_url)

    def test_flag_resources_in_different_xblocks(self):
        """
        Flag resources as problematic in two different xblocks
        """
        event_data = {'id': 0, 'isProblematic': True, 'reason': 'reason 0'}
        # Test
        for xblock_name in self.xblock_names:
            resp = self.call_event('flag_resource', event_data, xblock_name)
            self.assertEqual(resp['Success'], True)
            self.assertEqual(resp['reason'], 'reason 0')
            self.assert_request_status_code(200, self.course_url)

    def test_flag_resources_by_different_users(self):
        """
        Different users can't see the flag result of each other
        """
        event_data = {'id': 0, 'isProblematic': True, 'reason': 'reason 0'}
        self.call_event('flag_resource', event_data)
        self.logout()
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        # Test
        resp = self.call_event('flag_resource', event_data)
        # The second user won't see the reason provided by the first user
        self.assertNotIn('oldReason', resp)
        self.assertEqual(resp['Success'], True)
        self.assertEqual(resp['reason'], 'reason 0')
        self.assert_request_status_code(200, self.course_url)


class TestRecommenderUserIdentity(TestRecommender):
    """
    Check whether we can identify users correctly
    """
    def test_student_is_not_staff(self):
        """
        Verify student is not a staff
        """
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        url = self.get_handler_url('is_user_staff')
        result = json.loads(self.client.post(url, {}, '').content)
        self.assertFalse(result['is_user_staff'])
        self.assert_request_status_code(200, self.course_url)

    def test_staff_is_user_staff(self):
        """
        Verify staff is a staff
        """
        self.enroll_staff(self.staff_user)
        url = self.get_handler_url('is_user_staff')
        result = json.loads(self.client.post(url, {}, '').content)
        self.assertTrue(result['is_user_staff'])
        self.assert_request_status_code(200, self.course_url)


@ddt
class TestRecommenderFileUploading(TestRecommender):
    """
    Check whether we can handle file uploading correctly
    """
    def setUp(self):
        # call the setUp function from the superclass
        super(TestRecommenderFileUploading, self).setUp()

        # Fake S3 information
        self.s3_info = {
            'aws_access_key': 'access key',
            'aws_secret_key': 'secret key',
            'bucketName': 'bucket name',
            'uploadedFileDir': '/'
        }

    def attempt_upload_file_and_verify_result(self, test_case, xblock_name):
        """
        Running on a test case, creating a temp file, uploading it by
        calling the corresponding ajax event, and verifying that upload
        happens or is rejected as expected.
        """
        f_handler = StringIO.StringIO(test_case['magic_number'].decode('hex'))
        f_handler.content_type = test_case['mimetypes']
        f_handler.name = 'file' + test_case['suffixes']
        url = self.get_handler_url('upload_screenshot', xblock_name)
        response = self.client.post(url, {'file': f_handler})
        self.assertEqual(response.content, test_case['response'])
        self.assert_request_status_code(200, self.course_url)

    def test_set_s3_info(self):
        """
        Verify the s3 information setting
        """
        self.enroll_student(self.STUDENT_INFO[0][0], self.STUDENT_INFO[0][1])
        result = self.call_event('set_s3_info', self.s3_info)
        self.assertEqual(result['Success'], False)
        self.assert_request_status_code(200, self.course_url)

        self.logout()
        self.enroll_staff(self.staff_user)
        result = self.call_event('set_s3_info', self.s3_info)
        self.assertEqual(result['Success'], True)
        self.assert_request_status_code(200, self.course_url)

    @data({
        'suffixes': '.csv',
        'magic_number': 'ffff',
        'mimetypes': 'text/plain',
        'response': 'IMPROPER_S3_SETUP'
    })
    def test_upload_screenshot_s3_not_set(self, test_case):
        """
        Verify the file uploading fails correctly when the s3 is not set
        """
        self.enroll_staff(self.staff_user)
        self.attempt_upload_file_and_verify_result(test_case, self.xblock_names[0])
        self.assert_request_status_code(200, self.course_url)

    @data(
        {
            'suffixes': '.csv',
            'magic_number': 'ffff',
            'mimetypes': 'text/plain',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong extension name
        {
            'suffixes': '.gif',
            'magic_number': '89504e470d0a1a0a',
            'mimetypes': 'image/gif',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong magic number
        {
            'suffixes': '.jpg',
            'magic_number': '89504e470d0a1a0a',
            'mimetypes': 'image/jpeg',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong magic number
        {
            'suffixes': '.png',
            'magic_number': '474946383761',
            'mimetypes': 'image/png',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong magic number
        {
            'suffixes': '.jpg',
            'magic_number': '474946383761',
            'mimetypes': 'image/jpeg',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong magic number
        {
            'suffixes': '.png',
            'magic_number': 'ffd8ffd9',
            'mimetypes': 'image/png',
            'response': 'FILE_TYPE_ERROR'
        },  # Upload file with wrong magic number
        {
            'suffixes': '.gif',
            'magic_number': 'ffd8ffd9',
            'mimetypes': 'image/gif',
            'response': 'FILE_TYPE_ERROR'
        }
    )
    def test_upload_screenshot_wrong_file_type(self, test_case):
        """
        Verify the file uploading fails correctly when file with wrong type
        (extension/magic number) is provided
        """
        self.enroll_staff(self.staff_user)
        xblock_name = self.xblock_names[0]
        # Set fake s3 information for the first block
        # Assume correct, test in test_set_s3_info
        self.client.post(self.get_handler_url('set_s3_info', xblock_name), json.dumps(self.s3_info), '')
        # Upload file with wrong extension name or magic number
        self.attempt_upload_file_and_verify_result(test_case, xblock_name)
        self.assert_request_status_code(200, self.course_url)

    @data({
        'suffixes': '.csv',
        'magic_number': 'ffff',
        'mimetypes': 'text/plain',
        'response': 'IMPROPER_S3_SETUP'
    })
    def test_upload_screenshot_multiple_blocks(self, test_case):
        """
        Verify the s3 information setting and file uploading work independently
        in the two blocks
        """
        self.enroll_staff(self.staff_user)
        # Set fake s3 information for the first xblock
        # Assume correct, test in test_set_s3_info
        self.client.post(self.get_handler_url('set_s3_info', self.xblock_names[0]), json.dumps(self.s3_info), '')
        # Test on the second xblock
        self.attempt_upload_file_and_verify_result(test_case, self.xblock_names[1])
        self.assert_request_status_code(200, self.course_url)

    @data(
        {
            'suffixes': '.png',
            'magic_number': '89504e470d0a1a0a',
            'mimetypes': 'image/png',
            'response': 'IMPROPER_S3_SETUP'
        },
        {
            'suffixes': '.gif',
            'magic_number': '474946383961',
            'mimetypes': 'image/gif',
            'response': 'IMPROPER_S3_SETUP'
        },
        {
            'suffixes': '.gif',
            'magic_number': '474946383761',
            'mimetypes': 'image/gif',
            'response': 'IMPROPER_S3_SETUP'
        },
        {
            'suffixes': '.jpg',
            'magic_number': 'ffd8ffd9',
            'mimetypes': 'image/jpeg',
            'response': 'IMPROPER_S3_SETUP'
        }
    )
    def test_upload_screenshot_correct_file_type(self, test_case):
        """
        Verify the file type checking in the file uploading method is
        successful. We don't check whether the file is uploaded successfully
        to S3 or not. Thus, we still get 'IMPROPER_S3_SETUP' error here.
        """
        self.enroll_staff(self.staff_user)
        xblock_name = self.xblock_names[0]
        # Set fake s3 information for the first xblock
        # Assume correct, test in test_set_s3_info
        self.client.post(self.get_handler_url('set_s3_info', xblock_name), json.dumps(self.s3_info), '')
        # Upload file with correct extension name and magic number
        # It fails because we set fake s3 information here
        self.attempt_upload_file_and_verify_result(test_case, xblock_name)
        self.assert_request_status_code(200, self.course_url)
