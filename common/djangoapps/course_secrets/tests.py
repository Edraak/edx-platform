"""
Simple tests for the CourseSecrets app.
"""

from django.test import TestCase

from course_secrets import create_course_secret
from course_secrets.models import CourseSecret
from student.tests.factories import UserFactory


class CourseSecretMethodTests(TestCase):
    def test_anonymized_user_id_different_courses(self):
        """
        A user should have a different anonymized ID for each course.
        """
        COURSE_1 = 'edX/toy/2012_Fall'
        COURSE_2 = 'edx/full/6.002_Spring_2012'

        course_secret_1 = create_course_secret(COURSE_1)
        course_secret_2 = create_course_secret(COURSE_2)
        user = UserFactory.build(id=1)
        self.assertNotEqual(course_secret_1.anonymized_user_id(user),
                            course_secret_2.anonymized_user_id(user))


    def test_anonymized_user_id_different_users(self):
        """
        Different users should have different anonymized IDs in the
        same course.
        """
        course_secret = CourseSecret(secret="shhh", course_id="edX/111/Robot_Course")
        user_1 = UserFactory.build(id=1)
        user_2 = UserFactory.build(id=2)
        self.assertNotEqual(course_secret.anonymized_user_id(user_1),
                            course_secret.anonymized_user_id(user_2))

