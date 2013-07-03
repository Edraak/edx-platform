import json
from collections import defaultdict
from pprint import pformat

from django.conf import settings
from django.shortcuts import render_to_response

from courseware.models import StudentModule, StudentModuleHistory

def default(_request, course_id):
    if 'analytics' in settings.DATABASES:
        objects = StudentModuleHistory.objects.using('analytics')
    else:
        objects = StudentModuleHistory.objects

    problem_id = "i4x://MITx/2.01x/problem/HW1_1a"

    problems = objects.filter(student_module__course_id=course_id)
    problems = problems.filter(student_module__module_state_key=problem_id)
    problems = problems.filter(student_module__grade__isnull=False)

    problems = list(problems)

    values = defaultdict(list)
    for problem in problems:
        cm = json.loads(problem.state).get('student_answers', {})
        for k, v in cm.iteritems():
            values[k].append(v)

    data = {}
    for k, v in values.iteritems():
        data[k] = calculate_histogram(v)

    context = {
        'course_id': course_id,
        'problem_id': problem_id,
        'data': pformat(data)
    }

    return render_to_response('default.html', context)


def calculate_histogram(values):
    histogram = defaultdict(int)
    for v in values:
        histogram[v] += 1

    t = float(sum(histogram.values()))
    histogram = {k: (v, "{0:.2%}".format(v / t)) for k, v in histogram.iteritems()}

    return histogram
