from django.conf.urls import patterns, url
from edraak_forus.views import RegistrationApiView, AuthView


urlpatterns = patterns('',  # nopep8
    url(r'^v1/auth$', AuthView.as_view(), name='forus_v1_auth'),
    url('^v1/api/registration', RegistrationApiView.as_view(), name='forus_v1_reg_api'),
    url('^error', 'edraak_forus.views.error', name='forus_v1_error'),
)
