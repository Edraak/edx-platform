#!/usr/bin/python
"""
django management command: dump grades to csv files
for use by batch processes
"""
from xmodule.modulestore.django import modulestore
from instructor.offline_gradecalc import offline_grade_calculation
import multiprocessing.dummy as mp
from courseware import models
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "Compute grades for all students in all unproccessed courses, and store result in DB.\n"
    help += "Usage: compute_grades \n"

    def handle(self, *args, **options):
        today = timezone.now()
        all_courses = modulestore().get_courses()

        def condition(course):
            computed_course = models.OfflineComputedGradeLog.objects.filter(course_id=course.id)
            if not computed_course:  # if not processed before
                return True
            if course.end and today < course.end or course.is_self_paced():  # if curr of is_self_paced
                return (today - computed_course.latest().created).days > 7  # if not updated in the past 7 days
            return False

        courses = filter(condition, all_courses)

        print "processing {} courses ...".format(len(courses))

        p = mp.Pool(2)
        p.map(offline_grade_calculation, courses)
        p.close()
        p.join()
