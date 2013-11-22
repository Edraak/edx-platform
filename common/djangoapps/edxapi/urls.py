from django.conf.urls import url, patterns

urlpatterns = patterns('edxapi.views',  # nopep8
    url(r'^indexes/?$', 'list_indexes', name='list_indexes'),
    url(r'^indexes/(?P<index_id>[\w.]+)/?$', 'detail_index', name='detail_index'),
    url(r'^indexes/(?P<index_id>[\w.]+)/branches?$', 'index_branches', name='index_branches'),
    url(r'^indexes/(?P<index_id>[\w.]+)/branches/(?P<branch>\w+)?$', 'index_branch_redirect', name='index_branch_redirect'),
    url(r'^snapshots/(?P<snapshot_id>[\w.]+)/?$', 'detail_snapshot', name='detail_snapshot'),
    url(r'^snapshots/(?P<snapshot_id>[\w.]+)/xblocks?$', 'list_xblocks_in_snapshot', name='list_xblocks_in_snapshot'),
    url(r'^snapshots/(?P<snapshot_id>[\w.]+)/xblocks/(?P<xblock_name>[\w_]+)?$', 'detail_xblock_in_snapshot', name='detail_xblock_in_snapshot'),
)
