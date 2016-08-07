from django.db import models
from django.contrib.auth.models import User

from student.models import LoginFailures


class RateLimitedIP(models.Model):
    ip_address = models.GenericIPAddressField(primary_key=True)
    lockout_count = models.IntegerField(default=1, db_index=True)

    # This is informational, which aids search
    # In reality there could be many users for the same model, but I for now
    # need only the latest user.
    latest_user = models.ForeignKey(User, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __unicode__(self):
        return self.ip_address

    class Meta:
        """
        Rename the model and make it a bit more user-friendly.
        """

        verbose_name = 'IP-based Lock'
        verbose_name_plural = 'IP-based Lock'


class StudentAccountLock(LoginFailures):
    """
    Make a proxy/fake LoginFailures model, to organize the admin panel a bit.

    The name of the model is also adjusted to be user friendly.
    """

    class Meta:
        proxy = True
