import datetime
from optparse import make_option
from pytz import UTC

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from certificates.models import CertificateStatuses, certificate_status_for_student
from certificates.queue import XQueueCertInterface
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore


class Command(BaseCommand):

    help = """
    Generate new verification pages for every student receiving a certificate
    in a given course. Can optionally be run for just one student in one
    course.

    Give --user to regenerate verification for a specific user.

    Use the --noop option to test without actually putting verification
    requests on the queue.
    """

    option_list = BaseCommand.option_list + (
        make_option('-n', '--noop',
                    action='store_true',
                    dest='noop',
                    default=False,
                    help="Don't add certificate requests to the queue"),
        make_option('--insecure',
                    action='store_true',
                    dest='insecure',
                    default=False,
                    help="Don't use https for the callback url to the LMS, useful in http test environments"),
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=False,
                    help='Grade and generate certificates '
                    'for a specific course'),
        make_option('-f', '--force-gen',
                    metavar='STATUS',
                    dest='force',
                    default=False,
                    help='Will generate new certificates for only those users '
                    'whose entry in the certificate table matches STATUS. '
                    'STATUS can be downloadable, generating, unavailable, '
                    'deleted, error or notpassing.'),
    )

    def handle(self, *args, **options):

        # By default verifies certs in the downloadable state, can be set
        # to something else with the force flag.
        if options['force']:
            valid_statuses = getattr(CertificateStatuses, options['force'])
        else:
            valid_statuses = [CertificateStatuses.downloadable]

        if not options['course']:
            raise CommandError('course_id is required')
        course_id = options['course']

        # prefetch all chapters/sequentials by saying depth=2
        course = modulestore().get_instance(course_id, CourseDescriptor.id_to_location(course_id), depth=2)

        print "Fetching enrolled students for {0}".format(course_id)
        enrolled_students = User.objects.filter(
            courseenrollment__course_id=course_id).prefetch_related(
                "groups").order_by('username')

        # Print update after the lesser of 500 students or every 10%
        total = enrolled_students.count()
        interval = int(total * 0.1)
        if interval > 500:
            interval = 500
        count = 0
        print "{0} students enrolled in {1}, updates every {2} students".format(
                total, course_id, interval)

        # Connect to the xqueue
        xq = XQueueCertInterface()
        if options['insecure']:
            xq.use_https = False

        start = datetime.datetime.now(UTC)
        for student in enrolled_students:
            count += 1
            if count % interval == 0:
                # Print a status update with an approximation of
                # how much time is left based on how long the last
                # interval took
                diff = datetime.datetime.now(UTC) - start
                timeleft = diff * (total - count) / interval
                hours, remainder = divmod(timeleft.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                print "{0}/{1} completed ~{2:02}:{3:02}m remaining".format(
                    count, total, hours, minutes)
                start = datetime.datetime.now(UTC)

            if certificate_status_for_student(student, course_id)['status'] in valid_statuses:
                if not options['noop']:
                    # Add the certificate request to the queue
                    ret = xq.verify_cert(student, course_id, course=course)
                    if ret != '':
                        print '{0} - {1}'.format(student.username, ret)
