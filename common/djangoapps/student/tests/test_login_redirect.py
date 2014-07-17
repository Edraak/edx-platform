'''
Tests for redirect from the rendered login.html page
'''
from django.test import TestCase
from django.test.client import Client
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from student.tests.factories import UserFactory, RegistrationFactory, UserProfileFactory

class LoginRedirectTest(TestCase):
    '''
    Test redirect from the login page itself
    '''

    def test_login_next(self):

        email = 'test@edx.org'
        password = 'test_password'

        # Create a user and save it to the database
        self.user = UserFactory.build(username='test', email=email)
        self.user.set_password(password)
        self.user.save()

        # Create a registration for the user
        RegistrationFactory(user=self.user)

        # Create a profile for the user
        UserProfileFactory(user=self.user)

        # Create the test client
        self.client = Client()
        cache.clear()

        # The URL that we want to test
        self.url = '{}?next=/dashboard'.format(reverse('login'))

        post_params = {'email': email, 'password': password}
        result = self.client.post(self.url, post_params)
