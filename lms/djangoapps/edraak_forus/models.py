from django.db import models
from xmodule_django.models import CourseKeyField
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


class ForusProfileForNonStudentsError(Exception):
    pass


class ForusProfile(models.Model):
    user = models.ForeignKey(User, unique=True, db_index=True)
    # Translators: Edraak-specific
    date_created = models.DateTimeField(_('date forus profile created'), default=timezone.now)

    @staticmethod
    def create_for_user(user):

        if user.is_staff or user.is_superuser:
            # Translators: Edraak-specific
            raise ForusProfileForNonStudentsError(_("ForUs profile cannot be created for admins and staff."))

        forus_profile = ForusProfile(user=user)
        forus_profile.save()

    @staticmethod
    def is_forus_user(user):
        if not user:
            return False

        try:
            ForusProfile.objects.get(user=user)
        except ForusProfile.DoesNotExist:
            return False
        else:
            return True


class ForusPublishedCertificate(models.Model):
    user = models.ForeignKey(User)
    course_id = CourseKeyField(max_length=255, db_index=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)

    class Meta:
        unique_together = (('user', 'course_id'),)
        ordering = ('user', 'course_id')

    @classmethod
    def is_published(cls, user_id, course_id):
        return cls.objects.filter(user_id=user_id, course_id=course_id).count() > 0

    def __unicode__(self):
        return (
            "[ForusPublishedCertificate] {}: {} ({});"
        ).format(self.user, self.course_id, self.date_created)
