from django.conf.urls import patterns, url

urlpatterns = patterns(
    'edraak_api.views',
    url(r'^courses/$', 'courses'),
)
