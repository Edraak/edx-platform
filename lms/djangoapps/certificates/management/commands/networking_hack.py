"""Django management command to force certificate regeneration for one user"""

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from certificates.queue import XQueueCertInterface
from courseware.models import StudentModule
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore


class Command(BaseCommand):
    help = """Put a request on the queue to recreate the certificate for a particular user in a particular course."""

    option_list = BaseCommand.option_list + (
        make_option('-n', '--noop',
                    action='store_true',
                    dest='noop',
                    default=False,
                    help="Don't grade or add certificate requests to the queue"),
        make_option('-T', '--template',
                    metavar='TEMPLATE',
                    dest='template_file',
                    default=None,
                    help='The template file used to render this certificate, like "QMSE01-distinction.pdf"'),
    )

    def handle(self, *args, **options):

        template_file = options['template_file']
        if not template_file:
            raise CommandError('You must specify the alternate template to use for this cert.')
        course_id = 'Engineering/Networking/Winter2014'
        print "Fetching course data for {0}".format(course_id)
        xq = XQueueCertInterface()
        course = modulestore().get_instance(course_id, CourseDescriptor.id_to_location(course_id), depth=2)
        special_certs_exercises = list(StudentModule.objects.raw(
            "select sm.id,sm.student_id from courseware_studentmodule sm "
            "where sm.module_id='i4x://Engineering/Networking/problem/9491a32e51c046ebbaa0358d2d22789c' "
            "and sm.grade >= 0.8"))
        special_certs_students = [e.student for e in special_certs_exercises]

        for student in special_certs_students:

            if not options['noop']:
                # Add the certificate request to the queue
                ret = xq.regen_cert(student, course_id, course=course, 
                                    forced_grade=None,
                                    template_file=options['template_file'])
                print '{0} - {1}'.format(student, ret)
            else:
                print "noop option given, skipping work queueing for {0}".format(student)
