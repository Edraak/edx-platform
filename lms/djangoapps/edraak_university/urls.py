"""
URLs for the student support app.
"""
from django.conf.urls import patterns, url
from django.conf import settings

urlpatterns = patterns('',  # nopep8
    url(
       r'^id/{}$'.format(settings.COURSE_ID_PATTERN),
       'edraak_university.views.id_tab',
       name='edraak_university_id_tab'
    ),
)
