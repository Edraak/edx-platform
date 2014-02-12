#!/usr/bin/python
#
# CME management command: dump userinfo to csv files for reporting

import csv
from datetime import datetime
from optparse import make_option
import sys
import tempfile

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from pytz import UTC

from courseware.courses import get_course_by_id

from instructor.views.legacy import get_student_grade_summary_data


class Command(BaseCommand):
    help = """Export data required by Stanford SCCME Tracker Project to .csv file."""

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=False,
                    help='The course id (e.g., CME/001/2013-2015) to select from. Mutually exclusive with "--all"'),
        make_option('-a', '--all',
                    dest='all',
                    default=False,
                    help='Request all users dumped for all courses; mutually exclusive with "--course"'),
        make_option('-o', '--outfile',
                    metavar='OUTFILE',
                    dest='outfile',
                    default=False,
                    help='The file path to which to write the output.'),
    )


    def handle(self, *args, **options):

        course_id = options['course']
        do_all_courses = options['all']
        outfile_name = options['outfile']
        verbose = int(options['verbosity']) > 1

        if do_all_courses:
            raise CommandError('--all is not currently implemented; please use --course')
        if not (do_all_courses or course_id):
            raise CommandError('--course and --all are mutually exclusive')
        elif (do_all_courses and course_id):
            raise CommandError('One of --coure or --all must be given')
        outfile = None
        if outfile_name:
            outfile = open(outfile_name, 'wb')
        else:
            outfile = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
            outfile_name = outfile.name

        course = get_course_by_id(course_id)
        sys.stdout.write("Fetching enrolled students for {course}...".format(course=course_id))
        enrolled_students = User.objects.filter(courseenrollment__course_id=course_id).prefetch_related("groups").order_by('username').values()
        sys.stdout.write(" done.\n")

        count = 0
        total = enrolled_students.count()
        start = datetime.now(UTC)
        intervals = int(0.10 * total)
        if intervals > 100 and verbose:
            intervals = 100
        sys.stdout.write("Processing users")

        for student in enrolled_students:

            count += 1
            if count % intervals == 0:
                if verbose:
                    diff = datetime.now(UTC) - start
                    timeleft = diff * (total - count) / intervals
                    hours, remainder = divmod(timeleft.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    sys.stdout.write("\n{count}/{total} completed ~{hours:02}:{minutes:02} remaining\n".format(count=count, total=total, hours=hours, minutes=minutes))
                    start = datetime.now(UTC)
                else:
                    sys.stdout.write('.')

            print student
            import pdb; pdb.set_trace()


        print "-----------------------------------------------------------------------------"
        print "Dumping grades from %s to file %s (get_raw_scores=%s)" % (course.id, fn, get_raw_scores)
        datatable = get_student_grade_summary_data(request, course, course.id, get_raw_scores=get_raw_scores)

        fp = open(fn, 'w')

        writer = csv.writer(fp, dialect='excel', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(datatable['header'])
        for datarow in datatable['data']:
            encoded_row = [unicode(s).encode('utf-8') for s in datarow]
            writer.writerow(encoded_row)


        outfile.close()
        sys.stdout.write("Data written to {name}\n".format(name=outfile_name))
