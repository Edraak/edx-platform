from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns('',  # nopep8
                       url(r'^issue$', 'edraak_certificates.views.issue', name='edraak_certificates_issue'),

                       url(r'^download/{}$'.format(settings.COURSE_ID_PATTERN), 'edraak_certificates.views.download',
                           name='edraak_certificates_download'),

                       url(r'^preview/{}$'.format(settings.COURSE_ID_PATTERN), 'edraak_certificates.views.preview',
                           name='edraak_certificates_preview'),
)
