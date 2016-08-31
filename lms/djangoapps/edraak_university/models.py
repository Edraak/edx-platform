from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from xmodule_django.models import CourseKeyField


class UniversityID(models.Model):
    user = models.ForeignKey(User)
    course_key = CourseKeyField(max_length=255, db_index=True)
    university_id = models.CharField(max_length=100)
    section_number = models.CharField(max_length=10)
    date_created = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return u'{user} - {course_key} - {university_id}'.format(
            user=self.user,
            course_key=self.course_key,
            university_id=self.university_id,
        )

    class Meta:
        unique_together = ('user', 'course_key',)
