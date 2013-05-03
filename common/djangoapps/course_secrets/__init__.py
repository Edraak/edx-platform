import hashlib
import time

from django.conf import settings
from .models import CourseSecret

def create_course_secret(course_id):
    """
    Generates a secret key for use with this course, from which we'll
    derive further keys for hashing (anonymizing) usernames for data
    export.
    """
    secret = hashlib.sha1()

    # include the secret key as a salt, and to make the ids unique across
    # different LMS installs.
    secret.update(settings.SECRET_KEY)
    secret.update(str(course_id))
    secret.update(str(time.gmtime()))
    return CourseSecret.objects.create(secret=secret.hexdigest(), course_id=course_id)


