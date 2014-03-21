from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from exploded.daemon import StudentModuleHistoryDeDuper

class Command(BaseCommand):
    help = 'explodes studentmodulehistory items into a schema and stores them in the exploded db'

    option_list = BaseCommand.option_list + (make_option(
        '-c',
        '--course',
        action='store',
        dest='course_id',
        default=None,
        help='Limit the studentmodulehistory items processed to <COURSE_ID>'
    ),)
    def handle(self, *args, **options):
        print(options)
        if 'course_id' in options:
            print(options['course_id'])
        deduper = StudentModuleHistoryDeDuper()
        deduper.run_daemon(options['course_id'])
