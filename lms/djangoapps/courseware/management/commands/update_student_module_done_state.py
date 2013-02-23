#!/usr/bin/python
#
# django management command: update student module done state (for xmodules in grading context only)

import os, sys, string
import datetime
import json

from instructor.views import *
from courseware.courses import get_course_by_id
from xmodule.modulestore.django import modulestore

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "update StudentModule.done for modules in grading context of a specified course\n"
    help = "give two arguments:\n"
    help += "   course_id_or_dir: either course_id or course_dir\n"
    help += "   problem_id\n"

    def handle(self, *args, **options):

        print "args = ", args

        course_id = args[0]
        problem_id = args[1]

        try:
            course = get_course_by_id(course_id)
        except Exception as err:
            if course_id in modulestore().courses:
                course = modulestore().courses[course_id]
            else:
                print "-----------------------------------------------------------------------------"
                print "Sorry, cannot find course %s" % course_id
                print "Please provide a course ID or course data directory name, eg content-mit-801rq"
                return

        print "-----------------------------------------------------------------------------"
        print "updating problem %s for course %s" % (problem_id, course.id)
    
        if 1:
            (org, course_name, run)=course.id.split("/")
            module_state_key="i4x://"+org+"/"+course_name+"/problem/"+problem_id
            print "module_state_key=%s" % module_state_key
            smdat = StudentModule.objects.filter(course_id=course.id,
                                                 module_state_key=module_state_key)

            smdat = smdat.order_by('student')
            print "Found %d records to update" % len(smdat)
            ndone, nincomplete, nnotstarted = (0,0,0)
            for sm in smdat:
                try:
                    state = json.loads(sm.state)
                    done = state['done']
                    attempts = state['attempts']
                except Exception as err:
                    print "Oops error %s, state=%s" % (err,sm.state)
                    continue
                print "%s: sm.done=%s, done=%s, attempts=%s" % (sm, sm.done, done, attempts)
                if done:
                    sm.done = 'f'
                    ndone += 1
                elif attempts:
                    sm.done = 'i'
                    nincomplete += 1
                else:
                    sm.done = 'na'
                    nnotstarted += 1
                sm.save()
            print "Updated %d records" % len(smdat)
            print "ndone = %s" % ndone
            print "nincomplete = %s" % nincomplete
            print "nnotstarted = %s" % nnotstarted
            
                    
                
                