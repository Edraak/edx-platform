"""
Use the 'Dummy' auth provider for generic integration tests of third_party_auth.
"""
import unittest
from third_party_auth.tests import testutil

from .base import IntegrationTestMixin


@unittest.skipUnless(testutil.AUTH_FEATURE_ENABLED, testutil.AUTH_FEATURES_KEY + ' not enabled')
class GenericIntegrationTest(IntegrationTestMixin, testutil.TestCase):
    """
    Basic integration tests of third_party_auth using Dummy provider
    """
    PROVIDER_ID = "oa2-dummy"
    PROVIDER_NAME = "Dummy"
    PROVIDER_BACKEND = "dummy"

    USER_EMAIL = "adama@fleet.colonies.gov"
    USER_NAME = "William Adama"
    USER_USERNAME = "Galactica1"

    def setUp(self):
        super(GenericIntegrationTest, self).setUp()
        self.configure_dummy_provider(enabled=True)

    def do_provider_login(self, provider_redirect_url):
        """
        Mock logging in to the Dummy provider
        """
        # For the Dummy provider, the provider redirect URL is self.complete_url
        self.assertEqual(provider_redirect_url, self.url_prefix + self.complete_url)
        return self.client.get(provider_redirect_url)
