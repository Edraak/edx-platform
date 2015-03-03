from django.utils.translation import ugettext as _
from django.db import models, IntegrityError
from django.contrib.auth.models import User


class CourseTrackingCodeUsage(models.Model):
    user = models.ForeignKey(User)
    course_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (('user', 'course_id'),)

    @classmethod
    def record_usage(cls, user, course_id):
        view = cls(user=user, course_id=course_id)

        try:
            view.save()
        except IntegrityError as e:
            if u'duplicate entry' not in unicode(e):
                # This should ignore duplicate entry SQL errors, while keep failing on other potential errors
                raise

    def __unicode__(self):
        return _('{username} got tracked for {course_id}').format(
            username=self.user.username,
            course_id=self.course_id,
        )

    @classmethod
    def is_used(cls, user, course_id):
        return cls.objects.filter(user=user, course_id=course_id).count() > 0


class CourseTrackingCode(models.Model):
    course_id = models.CharField(max_length=255, db_index=True, unique=True, primary_key=True)
    code = models.TextField()

    def __unicode__(self):
        return _('{course_id} course confirmation code').format(course_id=self.course_id)

    @classmethod
    def get_tracking_code(cls, course_id):
        try:
            tracking_code = cls.objects.get(course_id=course_id)
            return tracking_code.code
        except cls.DoesNotExist:
            return ''

    @classmethod
    def get_tracking_code_once(cls, user, course_id):
        tracking_code = cls.get_tracking_code(course_id)

        if tracking_code:
            if not CourseTrackingCodeUsage.is_used(user, course_id):
                CourseTrackingCodeUsage.record_usage(user, course_id)
                return tracking_code

        return ''
