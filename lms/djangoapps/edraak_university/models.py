from django.db import models
from django.contrib.auth.models import User

from xmodule_django.models import CourseKeyField


class UniversityID(models.Model):
    user = models.OneToOneField(User)
    course_key = CourseKeyField(max_length=255, blank=True, db_index=True)
    university_id = models.CharField(max_length=100)
    section_number = models.CharField(max_length=10)

