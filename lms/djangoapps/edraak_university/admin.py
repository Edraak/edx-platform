"""
Django admin for university ID.
"""
from django.contrib import admin
from django.utils.html import escape
from django.core.urlresolvers import reverse

from student.models import UserProfile

from models import UniversityID, UniversityIDSetting
from edraak_forus.helpers import setfuncattr


class UniversityIDAdmin(admin.ModelAdmin):
    """Admin for University Student ID."""
    list_display = (
        'edraak_user',
        'course_key',
        'university_id',
        'edraak_profile',
        'email',
        'date_created',
    )

    readonly_fields = ('user', 'course_key', 'date_created',)
    search_fields = ('user__email', 'user__username', 'course_key', 'university_id',)

    @setfuncattr('allow_tags', True)
    def edraak_user(self, profile):
        user = profile.user
        return u'<a href="{url}">{name}</a>'.format(
            name=escape(user),
            url=reverse('admin:auth_user_change', args=[user.pk]),
        )

    @setfuncattr('allow_tags', True)
    def edraak_profile(self, profile):
        try:
            edraak_profile = UserProfile.objects.get(user=profile.user)
        except UserProfile.DoesNotExist:
            return None

        return u'<a href="{url}">Profile</a>'.format(
            url=reverse('admin:student_userprofile_change', args=[edraak_profile.pk]),
        )

    def email(self, profile):
        return profile.user.email

# UniversityIDSettings added to the admin panel
class UniversityIDSettingAdmin(admin.ModelAdmin):
    list_display=(
        'course_key',
        'registration_end_date',
        'terms_and_conditions_ar',
        'terms_and_conditions_en',
    )

    search_fields = ('course_key', 'registration_end_date',)


admin.site.register(UniversityID, UniversityIDAdmin)
admin.site.register(UniversityIDSetting, UniversityIDSettingAdmin)
