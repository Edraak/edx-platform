"""Unit tests for third_party_auth/pipeline.py."""

import random

from third_party_auth import pipeline
from third_party_auth.tests import testutil
import unittest


# Allow tests access to protected methods (or module-protected methods) under test.
# pylint: disable=protected-access


class MakeRandomPasswordTest(testutil.TestCase):
    """Tests formation of random placeholder passwords."""

    def setUp(self):
        super(MakeRandomPasswordTest, self).setUp()
        self.seed = 1

    def test_default_args(self):
        self.assertEqual(pipeline._DEFAULT_RANDOM_PASSWORD_LENGTH, len(pipeline.make_random_password()))

    def test_probably_only_uses_charset(self):
        # This is ultimately probablistic since we could randomly select a good character 100000 consecutive times.
        for char in pipeline.make_random_password(length=100000):
            self.assertIn(char, pipeline._PASSWORD_CHARSET)

    def test_pseudorandomly_picks_chars_from_charset(self):
        random_instance = random.Random(self.seed)
        expected = ''.join(
            random_instance.choice(pipeline._PASSWORD_CHARSET)
            for _ in xrange(pipeline._DEFAULT_RANDOM_PASSWORD_LENGTH))
        random_instance.seed(self.seed)
        self.assertEqual(expected, pipeline.make_random_password(choice_fn=random_instance.choice))


@unittest.skipUnless(testutil.AUTH_FEATURE_ENABLED, testutil.AUTH_FEATURES_KEY + ' not enabled')
class ProviderUserStateTestCase(testutil.TestCase):
    """Tests ProviderUserState behavior."""

    def test_get_unlink_form_name(self):
        google_provider = self.configure_google_provider(enabled=True)
        state = pipeline.ProviderUserState(google_provider, object(), None)
        self.assertEqual(google_provider.provider_id + '_unlink_form', state.get_unlink_form_name())
