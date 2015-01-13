"""
Django admin for conversion tracking.
"""
from django.contrib import admin
from .models import CourseTrackingCode, CourseTrackingCodeUsage


class CourseTrackingCodeAdmin(admin.ModelAdmin):
    pass


class CourseTrackingCodeUsageAdmin(admin.ModelAdmin):
    pass


admin.site.register(CourseTrackingCode, CourseTrackingCodeAdmin)
admin.site.register(CourseTrackingCodeUsage, CourseTrackingCodeUsageAdmin)
