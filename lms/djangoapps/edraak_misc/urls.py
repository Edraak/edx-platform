from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^check_student_grades/$', 'edraak_misc.views.check_student_grades', name='edraak_check_student_grades'),
    url(r'^all_courses/$', 'edraak_misc.views.all_courses', name='edraak_all_courses'),
)
