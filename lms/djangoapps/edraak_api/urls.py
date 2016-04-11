from django.conf.urls import patterns, url

urlpatterns = patterns(
    'edraak_api.views',
    url(r'^courses/$', 'courses', kwargs={'show_hidden': False}),
    url(r'^courses/with_hidden/$', 'courses', kwargs={'show_hidden': True}),
)
