from django.conf.urls import patterns, url
from .redirects import arabic_course_redirects
from .views import redirect_arabic_course

urlpatterns = patterns('')

for old_course_id, new_course_id in arabic_course_redirects:
    regex = ur'^(.*)({})(.*$)'.format(old_course_id)

    urlpatterns += (
        url(regex, redirect_arabic_course, {
            "new_course_id": new_course_id
        }),
    )
