"""
Models for Course Secrets

Migration Notes

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the mitx dir
2. django-admin.py schemamigration course_secrets --auto --settings=lms.envs.dev --pythonpath=. description_of_your_change
3. Add the migration file created in mitx/common/djangoapps/course_secrets/migrations/
"""

from django.db import models
from datetime import datetime
import hashlib

class CourseSecret(models.Model):
    """
    This model represents the per-course secrets, which are used as keys
    when hashing usernames/IDs for data export.
    """
    secret = models.CharField(max_length=255,
                              help_text="What is the secret? Shh!")
    course_id = models.CharField(max_length=255, db_index=True,
                                 help_text="Which course is this secret associated with?")
    created_at = models.DateTimeField(auto_now_add=True, default=datetime.now)
    updated_at = models.DateTimeField(auto_now=True, default=datetime.now)


    class Meta:
        unique_together = (("secret", "course_id"),)


    def anonymized_user_id(self, user):
        """
        Returns an anonymized user ID for exporting to third-party
        service providers like Qualtrics.
        """
        h = hashlib.sha1()
        h.update(self.secret)
        h.update(str(user.id))
        return h.hexdigest()


