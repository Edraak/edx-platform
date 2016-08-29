"""
URLs for the Edraak University ID app.
"""
from django.conf.urls import patterns, url
from django.conf import settings

import views



urlpatterns = patterns('',  # nopep8
    url(
       r'^id/{}$'.format(settings.COURSE_ID_PATTERN),
       'edraak_university.views.university_id',
       name='edraak_university_id',
    ),
    url(
       r'^id/{}/success$'.format(settings.COURSE_ID_PATTERN),
       views.UniversityIDSuccessView.as_view(),
       name='edraak_university_id_success',
    ),
    url(
        r'^id/{}/instructor/list$'.format(settings.COURSE_ID_PATTERN),
        views.UniversityIDListView.as_view(),
        name='edraak_university_id_list',
    ),
    url(
        r'^id/{}/instructor/update/(?P<pk>\d+)$'.format(settings.COURSE_ID_PATTERN),
        views.UniversityIDUpdateView.as_view(),
        name='edraak_university_id_update',
    ),
    url(
        r'^id/{}/instructor/delete/(?P<pk>\d+)$'.format(settings.COURSE_ID_PATTERN),
        views.UniversityIDDeleteView.as_view(),
        name='edraak_university_id_delete',
    ),
)
