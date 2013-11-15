from django.conf.urls import url, patterns

urlpatterns = patterns('edxapi.views',  # nopep8
    url(r'^indexes/?$', 'list_indexes', name='list_indexes'),
    url(r'^indexes/(?P<index_id>.*)/?$', 'detail_index', name='detail_index'),
)
