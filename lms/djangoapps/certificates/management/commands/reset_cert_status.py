from certificates.models import GeneratedCertificate
from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):

    help = """
    Reset certificates status to unavailble, filter by course, status, mode.
    """

    option_list = BaseCommand.option_list + (
        make_option('-n', '--noop',
                    action='store_true',
                    dest='noop',
                    default=False,
                    help="Print but do not update the GeneratedCertificate table"),
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    default=True,
                    help='Grade ungraded users for this course'),
        make_option('-s', '--status',
                    metavar='status',
                    dest='status',
                    default=False,
                    help='Status for the student, downloadable or notpassing'),
        make_option('-m', '--mode',
                    metavar='mode',
                    dest='mode',
                    default=False,
                    help='Mode for the student, honor, audit or verified'),
        )

    def handle(self, *args, **options):
        # Alias some variables
        course_id = options['course']
        status = options['status']
        mode = options['mode']
        # Course name is required for use
        if not course_id:
            options.error('Course Required')
        # Print out list
        print "Fetching for {0}".format(course_id)
        revoke = GeneratedCertificate.objects.filter(
            course_id__exact=course_id).filter(status__exact=status).filter(
            mode__exact=mode)

        for cert in revoke:
            # revoke by changing mode to unavailable
            print "Reseting".format(cert.user)
            cert.status = 'unavailable'
            if not options['noop']:
                cert.save()
