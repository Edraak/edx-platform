from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from openedx.core.djangoapps.course_groups.models import CourseUserGroup
from openedx.core.djangoapps.course_groups.cohorts import _get_default_cohort
from xmodule_django.models import CourseKeyField
from student.models import UserProfile


class UniversityID(models.Model):
    user = models.ForeignKey(User)
    course_key = CourseKeyField(max_length=255, db_index=True)
    university_id = models.CharField(verbose_name=_('Student University ID'), max_length=100)
    section_number = models.CharField(verbose_name=_('Section Number'), max_length=10)
    date_created = models.DateTimeField(default=timezone.now)
    cohort = models.ForeignKey(CourseUserGroup, null=True)
    can_edit = models.BooleanField(default=True)
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

    @classmethod
    def get_cohorts(cls, course_key):
        cohorts_choices = CourseUserGroup.objects.filter(course_id=course_key, group_type=CourseUserGroup.COHORT)

        # Exclude the default group
        default_group = _get_default_cohort(course_key)
        cohorts_choices = cohorts_choices.exclude(id=default_group.id)

        return cohorts_choices

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

    def __unicode__(self):
        return u'{user} - {course_key} - {university_id}'.format(
            user=self.user,
            course_key=self.course_key,
            university_id=self.university_id,
        )

    class Meta:
        unique_together = ('user', 'course_key',)


class UniversityIDSettings(models.Model):
    """
    This model stores university id settings for each course.
    """
    course_key = CourseKeyField(primary_key=True, max_length=255, db_index=True)
    registration_end_date = models.DateField(null=True, blank=True, verbose_name=_('Registration End Date'))
    terms_and_conditions = models.TextField(null=True, blank=True, verbose_name=_('Terms and Conditions'))

    def __unicode__(self):
        return unicode(self.course_key)
