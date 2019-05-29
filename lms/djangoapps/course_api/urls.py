"""
Course API URLs
"""
from django.conf import settings
from django.conf.urls import patterns, url, include

from .views import (
    CourseDetailView, CourseListView, MarketingCourseDetailView
)

# EDRAAK: if marketing site is enabled use the marketing details
if settings.FEATURES.get('ENABLE_MKTG_SITE'):
    course_detail_view = MarketingCourseDetailView.as_view()
else:
    course_detail_view = CourseDetailView.as_view()

urlpatterns = patterns(
    '',
    url(r'^v1/courses/$', CourseListView.as_view(), name="course-list"),
    url(r'^v1/courses/{}'.format(settings.COURSE_KEY_PATTERN), course_detail_view, name="course-detail"),
    url(r'', include('course_api.blocks.urls'))
)
