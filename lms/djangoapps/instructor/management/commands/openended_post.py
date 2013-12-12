#!/usr/bin/python
#
# django management command: dump grades to csv files
# for use by batch processes

from instructor.offline_gradecalc import offline_grade_calculation
from courseware.courses import get_course_by_id
from xmodule.modulestore.django import modulestore
from courseware.models import StudentModule
from courseware.model_data import FieldDataCache
from courseware.module_render import get_module, get_module_for_descriptor
from django.contrib.auth.models import User
from ...utils import create_module, get_descriptor, DummyRequest

from django.core.management.base import BaseCommand

import csv

def read_csv(path_to_csv):
    """
    reads a csv and returns a list
    """
    pass

def get_submission_from_state(module):
    """
    deserializes state and pulls out the submission (with <br> tags instead of '\n's)
    """
    pass

class Command(BaseCommand):
    help = "Usage: posts problem to xqueue \n"

    def handle(self, *args, **options):

        print "args = ", args

        if len(args) > 0:
            course_id = args[0]
            location = args[1]
            affected_students_ids = read_csv(args[2])
        else:
            print self.help
            return

        request = DummyRequest()
        course = get_course_by_id(course_id)
        descriptor = get_descriptor(course, location)
        if descriptor is None:
            print "Location not found in course"
            return


        affected_students = User.objects.filter(
            id__in=affected_students_ids,
            courseenrollment__is_active=1
        ).prefetch_related("groups").order_by('username')



        for student in affected_students:
            request.user = student
            request.session = {}

            try:
                student_module = StudentModule.objects.get(
                    student=student,
                    course_id=course_id,
                    module_state_key=descriptor.id
                )
                # print student_module

            except StudentModule.DoesNotExist:
                # student_module = None
                # do nothing
                pass

            # TODO: find the submission from relevant student states
            # (say a list of their ids)

            submission = get_submission_from_state(student_module.state)

            module.send_to_grader(submission, student_module.system)

