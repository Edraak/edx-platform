# Computes the data needed to display on the Instructor Dashboard

import json
import time

from json import JSONEncoder
from courseware import grades, models
from courseware.courses import get_course_by_id
from django.db.models import Count
from queryable import StudentModuleExpand

#Might not need all of these
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.inheritance import own_metadata


def get_problem_grade_distribution(course_id):
    """Returns the grade distribution per problem for the course

    Output is a dicts, where the key is the problem module_id and the value is a dict with:
    max_grade - max grade for this problem
    grade_distrib - array of tuples (<grade>,<count>).

    """

    # select module_id, grade, max_grade, count(*) as count from courseware_studentmodule where grade is not null and module_type = "problem" and module_id like "%<Course number>%" group by module_id, grade order by module_id, grade;
    db_query = models.StudentModule.objects.filter(course_id__exact=course_id, grade__isnull=False, module_type__exact="problem").values('module_state_key','grade','max_grade').annotate(count_grade=Count('grade'))

    prob_grade_distrib = {}
    for row in db_query:
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

def get_prob_attempt_distrib(course_id,max_attempts=10):
    """Returns the attempt (between 1-10+) distribution per problem for the course

    Output is a dicts, where the key is the problem module_id and the value is an array where the first index is
    the number of students that only attempted once, second is two times, etc. The 11th index is all students that
    attempted more than ten times.
    """

    db_query = StudentModuleExpand.objects.filter(course_id__exact=course_id, attempts__isnull=False, module_type__exact="problem").values('module_state_key','attempts').annotate(count_attempts=Count('attempts'))

    prob_attempts_distrib = {}
    for row in db_query:
        if row['module_state_key'] not in prob_attempts_distrib:
            prob_attempts_distrib[row['module_state_key']] = [0] * (max_attempts+1)

        if row['attempts'] > max_attempts:
            prob_attempts_distrib[row['module_state_key']][max_attempts] += row['count_attempts']
        else:
            prob_attempts_distrib[row['module_state_key']][row['attempts']-1] = row['count_attempts']

    return prob_attempts_distrib

def get_sequential_open_distrib(course_id):
    """Returns the number of students that opened each subsection/sequential of the course

    Outputs a dict mapping the module id to the number of students that have opened that subsection/sequential.
    """

    db_query = models.StudentModule.objects.filter(course_id__exact=course_id, module_type__exact="sequential").values('module_state_key').annotate(count_sequential=Count('module_state_key'))

    sequential_open_distrib = {}
    for row in db_query:
        squential_open_distrib[row['module_state_key']] = row['count_sequential']

    return sequential_open_distrib

def get_d3_problem_grade_distribution(course_id):
    prob_grade_distrib = get_problem_grade_distribution(course_id)

    # Get info on where each problem is
    course = modulestore().get_item(CourseDescriptor.id_to_location(course_id), depth=4)
    dict_id_to_display_names = {}
    cPosition = 0
    cSection = 0
    for section in course.get_children():
        cSection += 1
        sectionName = own_metadata(section)['display_name']
        cSubsection = 0
        for subsection in section.get_children():
            cSubsection += 1
            subsectionName = own_metadata(subsection)['display_name']
            cUnit = 0
            for unit in subsection.get_children():
                cUnit += 1
                unitName = own_metadata(unit)['display_name']
                cProblem = 0
                for child in unit.get_children():
                    if child.location.category == 'problem':
                        cProblem += 1
                        problemName = own_metadata(child)['display_name']
                        dict_id_to_display_names[child.location.url()] = {
                            'label': "{0}.{1}.{2}.{3}: {4}".format(cSection,cSubsection,cUnit,cProblem,problemName),
                            'detail': "{0}: {1}: {2}: {3}".format(sectionName, subsectionName, unitName, problemName),
                            'position': cPosition,
                            }
                        cPosition += 1
    
    d3_data = []

    for prob_id, value in prob_grade_distrib.iteritems():
        max_grade = float(value['max_grade'])
        
        label = "???"
        detail = "???"
        position = -1
        if prob_id in dict_id_to_display_names:
            detail = dict_id_to_display_names[prob_id]['detail']
            label = dict_id_to_display_names[prob_id]['label']
            position = dict_id_to_display_names[prob_id]['position']
        else:
            print "Can't find this id: ", prob_id
            
        stack_data = []
        for (grade,count_grade) in value['grade_distrib']:
            percent = (grade*100.0)/max_grade

            bar = {
                'color' : percent,
                'value' : count_grade,
                'tooltip' : "{0} - {1} students ({2:.0f}%)".format(detail, count_grade, percent),
                }
            stack_data.append(bar)

        stack = {
            'xValue' : label,
            'stackData' : stack_data,
            'position' : position
            }
        d3_data.append(stack)

    return sorted(d3_data, key=lambda stack: stack['position'])
