"""
Django admin page for ForUs models
"""
from django.contrib import admin
from .models import ForusProfile, ForusPublishedCertificate


class ForusProfileAdmin(admin.ModelAdmin):
    """Admin for ForUs profile."""
    list_display = ('user', 'date_created')


class ForusPublishedCertificateAdmin(admin.ModelAdmin):
    """Admin for ForUs published certificate."""
    list_display = ('user', 'course_id', 'date_created',)


admin.site.register(ForusProfile, ForusProfileAdmin)
admin.site.register(ForusPublishedCertificate, ForusPublishedCertificateAdmin)
