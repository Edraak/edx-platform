from django.conf.urls import patterns, url
from django.conf import settings


urlpatterns = patterns('',
    url(
        r'^get_student_email_for_bayt$',
        'edraak_bayt.views.get_student_email',
        name='edraak_bayt_get_student_email',
    ),
    url(
        r'^bayt-activation$',
        'edraak_bayt.views.activation',
        name='bayt_activation',
    ),
    url(
        r'^bayt/check-email/{}/(?P<email>.*)$'.format(settings.COURSE_ID_PATTERN),
        'edraak_bayt.views.check_email',
        name='bayt_check_email',
    ),
)
