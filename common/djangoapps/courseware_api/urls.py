from django.conf.urls.defaults import *
from tastypie.profile import ProfileResource
from tastypie.course import CourseResource

profile_resource = ProfileResource()
course_resource = CourseResource()

urlpatterns = patterns('',
    (r'^', include(profile_resource.urls)),
    (r'^', include(course_resource.urls)),
)

