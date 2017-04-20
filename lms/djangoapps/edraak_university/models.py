from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _, get_language

from student.models import UserProfile

from xmodule_django.models import CourseKeyField

class UniversityID(models.Model):
    user = models.ForeignKey(User)
    course_key = CourseKeyField(max_length=255, db_index=True)
    university_id = models.CharField(verbose_name=_('Student University ID'), max_length=100)
    section_number = models.CharField(verbose_name=_('Section Number'), max_length=10)
    date_created = models.DateTimeField(default=timezone.now)
    terms_and_conditions_read = models.BooleanField(default=False)
    # Will be used in `get_marked_university_ids()` method to mark
    # duplicate entries.
    is_conflicted = False

    def get_full_name(self):
        try:
            user_profile = UserProfile.objects.get(user=self.user)
            return user_profile.name
        except UserProfile.DoesNotExist:
            return None

    def get_email(self):
        return self.user.email

    def __unicode__(self):
        return u'{user} - {course_key} - {university_id}'.format(
            user=self.user,
            course_key=self.course_key,
            university_id=self.university_id,
        )

    @classmethod
    def get_marked_university_ids(cls, course_key):
        queryset = cls.objects.filter(course_key=course_key)
        queryset = queryset.order_by('university_id')

        def cleanup_id(id):
            """
            Trim an ID to make it easier to compare.
            """
            return id.strip().lower()

        entries = list(queryset)
        for i, entry in enumerate(entries):
            if i > 0:  # Avoid IndexError
                prev_entry = entries[i-1]
                if cleanup_id(entry.university_id) == cleanup_id(prev_entry.university_id):
                    entry.is_conflicted = True
                    prev_entry.is_conflicted = True

        return entries

    class Meta:
        unique_together = ('user', 'course_key',)

# Class related to university ID settings for a course
class UniversityIDSetting(models.Model):
    course_key = CourseKeyField(max_length=255, db_index=True)
    registration_end_date = models.DateTimeField(default=None, null=True, blank=True)
    terms_and_conditions_ar = models.TextField(null=True, blank=True)
    terms_and_conditions_en = models.TextField(null=True, blank=True)

    def get_terms_and_conditions(self):
        if get_language() == 'ar':
            return self.terms_and_conditions_ar
        else:
            return self.terms_and_conditions_en
