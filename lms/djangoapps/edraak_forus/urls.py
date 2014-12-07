from django.conf.urls import patterns, url

urlpatterns = patterns('',  # nopep8
    url(r'^v1/auth$', 'edraak_forus.views.auth', name="forus_v1_auth"),
    url(r'^create_account$', 'edraak_forus.views.create_account', name="forus_create_account"),
)
