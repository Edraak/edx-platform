"""
Unit tests for third_party_auth LTI auth providers
"""

import unittest
from oauthlib.common import Request
from third_party_auth.lti import LTIAuthBackend, LTI_PARAMS_KEY
from third_party_auth.tests.testutil import ThirdPartyAuthTestMixin
from social_core.tests.models import TestStorage
from social_core.tests.strategy import TestStrategy


class UnitTestLTI(unittest.TestCase, ThirdPartyAuthTestMixin):
    """
    Unit tests for third_party_auth LTI auth providers
    """

    def setUp(self):
        super(UnitTestLTI, self).setUp()
        self.strategy = TestStrategy(TestStorage)

    def test_get_user_details_missing_keys(self):
        lti = LTIAuthBackend(self.strategy)
        details = lti.get_user_details({LTI_PARAMS_KEY: {
            'lis_person_name_full': 'Full name'
        }})
        self.assertEquals(details, {
            'fullname': 'Full name'
        })

    def test_get_user_details_extra_keys(self):
        lti = LTIAuthBackend(self.strategy)
        details = lti.get_user_details({LTI_PARAMS_KEY: {
            'lis_person_name_full': 'Full name',
            'lis_person_name_given': 'Given',
            'lis_person_name_family': 'Family',
            'email': 'user@example.com',
            'other': 'something else'
        }})
        self.assertEquals(details, {
            'fullname': 'Full name',
            'first_name': 'Given',
            'last_name': 'Family',
            'email': 'user@example.com'
        })

    def test_get_user_id(self):
        lti = LTIAuthBackend(self.strategy)
        user_id = lti.get_user_id(None, {LTI_PARAMS_KEY: {
            'oauth_consumer_key': 'consumer',
            'user_id': 'user'
        }})
        self.assertEquals(user_id, 'consumer:user')

    def test_validate_lti_valid_request(self):
        request = Request(
            uri='https://example.com/lti',
            http_method='POST',
            body=self.read_data_file('lti_valid_request.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436823554,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertTrue(parameters)
        self.assertDictContainsSubset({
            'custom_extra': 'parameter',
            'user_id': '292832126'
        }, parameters)

    def test_validate_lti_valid_request_with_get_params(self):
        request = Request(
            uri='https://example.com/lti?user_id=292832126&lti_version=LTI-1p0',
            http_method='POST',
            body=self.read_data_file('lti_valid_request_with_get_params.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436823554,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertTrue(parameters)
        self.assertDictContainsSubset({
            'custom_extra': 'parameter',
            'user_id': '292832126'
        }, parameters)

    def test_validate_lti_old_timestamp(self):
        request = Request(
            uri='https://example.com/lti',
            http_method='POST',
            body=self.read_data_file('lti_old_timestamp.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436900000,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertFalse(parameters)

    def test_validate_lti_invalid_signature(self):
        request = Request(
            uri='https://example.com/lti',
            http_method='POST',
            body=self.read_data_file('lti_invalid_signature.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436823554,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertFalse(parameters)

    def test_validate_lti_cannot_add_get_params(self):
        request = Request(
            uri='https://example.com/lti?custom_another=parameter',
            http_method='POST',
            body=self.read_data_file('lti_cannot_add_get_params.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436823554,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertFalse(parameters)

    def test_validate_lti_garbage(self):
        request = Request(
            uri='https://example.com/lti',
            http_method='POST',
            body=self.read_data_file('lti_garbage.txt')
        )
        parameters = LTIAuthBackend._get_validated_lti_params_from_values(  # pylint: disable=protected-access
            request=request, current_time=1436823554,
            lti_consumer_valid=True, lti_consumer_secret='secret',
            lti_max_timestamp_age=10
        )
        self.assertFalse(parameters)
