from ratelimitbackend.backends import RateLimitMixin
from ratelimitbackend.exceptions import RateLimitException
from django.db.models import F

from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

from .models import RateLimitedIP


class EdraakRateLimitMixin(RateLimitMixin):
    """
    Make the limit a little bit more permissive.
    """
    minutes = 5
    requests = 100  # Make the limit a little bit more permissive

    def db_log_failed_attempt(self, ip_address, username=None):
        user = None

        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                pass

        try:
            limited_ip = RateLimitedIP.objects.get(ip_address=ip_address)
            limited_ip.lockout_count = F('lockout_count') + 1
        except RateLimitedIP.DoesNotExist:
            limited_ip = RateLimitedIP(ip_address=ip_address)

        limited_ip.latest_user = user
        limited_ip.save()


class EdraakRateLimitModelBackend(EdraakRateLimitMixin, ModelBackend):
    """
    Log the locks in the database and allow fine-grained unlock.
    """

    def authenticate(self, **kwargs):
        try:
            return super(EdraakRateLimitModelBackend, self).authenticate(**kwargs)
        except RateLimitException:
            request = kwargs.get('request')
            self.db_log_failed_attempt(
                ip_address=request.META['REMOTE_ADDR'],
                username=kwargs[self.username_key],
            )

            raise  # Keep it consistent with the RateLimitMixin logic
