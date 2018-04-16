from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns('',  # nopep8
                       url(
                           r'^issue/{}$'.format(settings.COURSE_ID_PATTERN),
                           'edraak_certificates.views.issue',
                           name='edraak_certificates_issue'
                       ),
                       url(
                           r'^check/{}$'.format(settings.COURSE_ID_PATTERN),
                           'edraak_certificates.views.check_status',
                           name='edraak_certificates_check_status'
                       ),
                       url(
                           r'^download/{}$'.format(settings.COURSE_ID_PATTERN),
                           'edraak_certificates.views.download',
                           name='edraak_certificates_download'
                       ),
)
