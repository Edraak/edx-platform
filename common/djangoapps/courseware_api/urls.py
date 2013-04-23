from django.conf.urls.defaults import *
from tastypie.profile import ProfileResource
from tastypie.course import CourseResource
from tastypie.xblock_api import XBlockResource
from tastypie.user import UserResource

profile_resource = ProfileResource()
course_resource = CourseResource()
xblock_resource = XBlockResource()
user_resource = UserResource()

urlpatterns = patterns('',
    (r'^', include(profile_resource.urls)),
    (r'^', include(course_resource.urls)),
    (r'^', include(xblock_resource.urls)),
    (r'^', include(user_resource.urls)),
)

