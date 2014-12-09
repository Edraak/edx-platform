"""
Django admin page for ForUs models
"""
from django.contrib import admin
from .models import ForusProfile


class ForusProfileAdmin(admin.ModelAdmin):
    """Admin for ForUs profile."""
    list_display = ('user', 'date_created')


admin.site.register(ForusProfile, ForusProfileAdmin)
