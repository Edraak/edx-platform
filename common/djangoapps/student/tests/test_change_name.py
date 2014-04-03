"""
Unit tests for change_name view of student.
"""
import json

from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test import TestCase

from student.tests.factories import UserFactory
from student.models import UserProfile


class TestChangeName(TestCase):
    """
    Check the change_name view of student.
    """
    def setUp(self):
        self.student = UserFactory.create(password='test')
        self.client = Client()

    def test_change_name_get_request(self):
        """Get requests are not allowed in this view."""
        resp = self.client.get(reverse('change_name'))
        self.assertEquals(resp.status_code, 405)

    def test_unauthenticated(self):
        """Unauthenticated user is not allowed to call this view."""
        resp = self.client.post(reverse('change_name'), {
            'new_name': 'waqas',
            'rationale': 'change identity'
        })
        self.assertEquals(resp.status_code, 404)

    def test_change_name_post_request(self):
        """Name will be changed when provided with proper data."""
        self.client.login(username=self.student.username, password='test')
        resp = self.client.post(reverse('change_name'), {
            'new_name': 'waqas',
            'rationale': 'change identity'
        })
        response_data = json.loads(resp.content)
        user = UserProfile.objects.get(user=self.student.id)
        meta = json.loads(user.meta)
        self.assertEquals(user.name, 'waqas')
        self.assertEqual(meta['old_names'][0][1], 'change identity')
        self.assertTrue(response_data['success'])

    def test_change_name_without_name(self):
        """Empty string for name is not allowed in this view."""
        self.client.login(username=self.student.username, password='test')
        resp = self.client.post(reverse('change_name'), {
            'new_name': '',
            'rationale': 'change identity'
        })
        response_data = json.loads(resp.content)
        self.assertFalse(response_data['success'])
