"""Common utility for testing third party oauth2 features."""
import json

import httpretty

from django.conf import settings
from provider.constants import PUBLIC
from provider.oauth2.models import Client
from social_django.models import UserSocialAuth
from social_core.backends.facebook import FacebookOAuth2

from student.tests.factories import UserFactory

from .testutil import ThirdPartyAuthTestMixin


@httpretty.activate
class ThirdPartyOAuthTestMixin(ThirdPartyAuthTestMixin):
    """
    Mixin with tests for third party oauth views. A TestCase that includes
    this must define the following:

    BACKEND: The name of the backend from python-social-auth
    USER_URL: The URL of the endpoint that the backend retrieves user data from
    UID_FIELD: The field in the user data that the backend uses as the user id
    """
    def setUp(self, create_user=True):
        super(ThirdPartyOAuthTestMixin, self).setUp()
        self.social_uid = "test_social_uid"
        self.access_token = "test_access_token"
        self.client_id = "test_client_id"
        self.oauth_client = Client.objects.create(
            client_id=self.client_id,
            client_type=PUBLIC
        )
        if create_user:
            self.user = UserFactory()
            UserSocialAuth.objects.create(user=self.user, provider=self.BACKEND, uid=self.social_uid)
        if self.BACKEND == 'google-oauth2':
            self.configure_google_provider(enabled=True)
        elif self.BACKEND == 'facebook':
            self.configure_facebook_provider(enabled=True)

    def _setup_provider_response(self, success=False, email=''):
        """
        Register a mock response for the third party user information endpoint;
        success indicates whether the response status code should be 200 or 400
        """
        if success:
            status = 200
            response = {self.UID_FIELD: self.social_uid}
            if email:
                response.update({'email': email})
            body = json.dumps(response)
        else:
            status = 400
            body = json.dumps({})

        self._setup_provider_response_with_body(status, body)

    def _setup_provider_response_with_body(self, status, body):
        """
        Register a mock response for the third party user information endpoint with given status and body.
        """
        httpretty.register_uri(
            httpretty.GET,
            self.USER_URL,
            body=body,
            status=status,
            content_type="application/json"
        )


class ThirdPartyOAuthTestMixinFacebook(object):
    """Tests oauth with the Facebook backend"""
    BACKEND = "facebook"
    USER_URL = FacebookOAuth2.USER_DATA_URL.format(version=settings.FACEBOOK_API_VERSION)
    # In facebook responses, the "id" field is used as the user's identifier
    UID_FIELD = "id"


class ThirdPartyOAuthTestMixinGoogle(object):
    """Tests oauth with the Google backend"""
    BACKEND = "google-oauth2"
    USER_URL = "https://www.googleapis.com/plus/v1/people/me"
    # In google-oauth2 responses, the "email" field is used as the user's identifier
    UID_FIELD = "email"
