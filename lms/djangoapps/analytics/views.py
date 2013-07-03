from django.conf import settings
from django.shortcuts import render_to_response

from courseware.models import StudentModule

def default(_request, course_id):
    if 'analytics' in settings.DATABASES:
        objects = StudentModule.objects.using('analytics')
    else:
        objects = StudentModule.objects

    count = objects.filter(course_id=course_id).count()
    context = {'msg': "{0} has {1}".format(course_id, count)}
    return render_to_response('default.html', context)
