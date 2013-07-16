# Computes the data needed to display on the Instructor Dashboard

import json
import time

from json import JSONEncoder
from courseware import grades, models
from courseware.courses import get_course_by_id
from django.db.models import Count

def get_problem_grade_distribution(course_id):
    """Returns the grade distribution per problem for the course

    Output is a dicts, where the key is the problem module_id and the value is a dict with:
    max_grade - max grade for this problem
    grade_distrib - array of tuples (<grade>,<count>).

    """

    print "Finding problem grade distribution for course_id=%s", course_id

    # select module_id, grade, max_grade, count(*) as count from courseware_studentmodule where grade is not null and module_type = "problem" and module_id like "%<Course number>%" group by module_id, grade order by module_id, grade;
    db_query = models.StudentModule.objects.filter(course_id__exact=course_id, grade__isnull=False, module_type__exact="problem").values('module_state_key','grade','max_grade').annotate(count_grade=Count('grade')).order_by('module_state_key','grade')

    prob_grade_distrib = {}
    for row in db_query:
        print row
        if row['module_state_key'] in prob_grade_distrib:
            prob_grade_distrib[row['module_state_key']]['grade_distrib'].append((row['grade'],row['count_grade']))
            if (prob_grade_distrib[row['module_state_key']]['max_grade'] != row['max_grade']) and (prob_grade_distrib[row['module_state_key']]['max_grade'] < row['max_grade']):
                prob_grade_distrib[row['module_state_key']]['max_grade'] = row['max_grade']
        else:
            prob_grade_distrib[row['module_state_key']] = {
                'max_grade' : row['max_grade'],
                'grade_distrib' : [(row['grade'],row['count_grade'])]
                }

    return prob_grade_distrib
