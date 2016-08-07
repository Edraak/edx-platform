from dateutil.relativedelta import relativedelta
import datetime

from django.core.cache import cache
from django.contrib.admin import DateFieldListFilter
from django.contrib import admin

from .models import RateLimitedIP, StudentAccountLock
from .backends import EdraakRateLimitModelBackend


class FakeRequest(object):
    def __init__(self, ip_address):
        self.META = {
            'REMOTE_ADDR': ip_address,
        }


class RateLimitedIPAdmin(admin.ModelAdmin):
    actions = ['reset_attempts']

    readonly_fields = (
        'ip_address',
        'latest_user',
        'created_at',
        'updated_at',
        'lockout_count',
    )

    list_display = (
        '__unicode__',
        'latest_user',
        'lockout_count',
        'lockout_duration',
        'unlock_time',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'ip_address',
        'latest_user__username',
        'latest_user__email',
    )

    list_filter = (
        ('updated_at', DateFieldListFilter),
    )

    ordering = ('-updated_at',)

    def lockout_duration(self, obj):
        delta = relativedelta(obj.updated_at, obj.created_at)
        periods = ('years', 'months', 'days', 'hours', 'minutes', 'seconds',)

        for period in periods:
            if hasattr(delta, period):
                count = getattr(delta, period)

                if count:
                    return '{count} {period}'.format(
                        count=count,
                        period=period,
                    )

    def unlock_time(self, obj):
        unlock_duration = datetime.timedelta(minutes=EdraakRateLimitModelBackend.minutes)
        return obj.updated_at + unlock_duration

    def get_actions(self, request):
        actions = super(RateLimitedIPAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def reset_attempts(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def delete_model(self, request, obj):
        backend = EdraakRateLimitModelBackend()
        cache_keys = backend.keys_to_check(request=FakeRequest(obj.ip_address))
        cache.delete_many(cache_keys)
        obj.delete()


class StudentAccountLockAdmin(admin.ModelAdmin):
    search_fields = (
        'user__email', 'user__username', 'user__pk',
    )

    readonly_fields = (
        'user', 'failure_count', 'lockout_until',
    )

    list_display = (
        'email', 'username', 'failure_count', 'lockout_until',
    )

    def email(self, login_failures):
        return login_failures.user.email

    def username(self, login_failures):
        return login_failures.user.username


admin.site.register(StudentAccountLock, StudentAccountLockAdmin)

admin.site.register(RateLimitedIP, RateLimitedIPAdmin)
