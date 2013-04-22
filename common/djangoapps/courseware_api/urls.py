from django.conf.urls.defaults import *
from tastypie.api import ProfileResource

profile_resource = ProfileResource()

urlpatterns = patterns('',
    (r'^', include(profile_resource.urls)),
)
