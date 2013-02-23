#!/usr/bin/python
#
# django management command: print grading context (ie which modules are graded)

import os, sys, string
import datetime
import json

from instructor.views import *
from courseware.courses import get_course_by_id
from xmodule.modulestore.django import modulestore

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "list modules which are to be graded, for a specified course\n"
    help = "give one argument:\n"
    help += "   course_id_or_dir: either course_id or course_dir\n"

    def handle(self, *args, **options):

        print "args = ", args

        course_id = args[0]

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
        print "Course grader:"
        
        print course.grader.__class__
        graders = {}
        if 'WeightedSubsectionsGrader' in str(course.grader.__class__):
            print
            print "Graded sections:"
            for subgrader, category, weight in course.grader.sections:
                print "  subgrader=%s, type=%s, category=%s, weight=%s" % (subgrader, subgrader.type, category, weight)
                subgrader.index = 1
                graders[subgrader.type] = subgrader

        print "-----------------------------------------------------------------------------"
        print "Listing grading context for course %s" % course.id
    
        gc = course.grading_context

        print "graded sections:" 
        
        print gc['graded_sections'].keys()

        for (gs, gsvals) in gc['graded_sections'].items():
            print "--> Section %s:" % (gs)
            for sec in gsvals:
                s = sec['section_descriptor']
                format = s.metadata.get('format')
                aname = ''
                if format in graders:
                    g = graders[format]
                    aname = '%s %02d' % (g.short_label, g.index)
                    g.index += 1
                elif s.display_name in graders:
                    g = graders[s.display_name]
                    aname = '%s' % g.short_label
                notes = ''
                if s.metadata.get('score_by_attempt',False):
                    notes = ', score by attempt!'
                print "      %s (format=%s, Assignment=%s%s)" % (s.display_name, format, aname, notes)

        print "all descriptors:"
        print "length=%d" % len(gc['all_descriptors'])
    
        
