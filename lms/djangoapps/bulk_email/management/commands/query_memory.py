from optparse import make_option
from textwrap import dedent

from django.core.management.base import BaseCommand, CommandError

from courseware.courses import get_course
from bulk_email.tasks import _get_recipient_queryset
from memory_profiler import profile
from instructor_task.subtasks import _generate_items_for_subtask
import math

class Command(BaseCommand):
    """
    testing memory usage

    """
    help = dedent(__doc__).strip()
    option_list = BaseCommand.option_list + (
        make_option('--course',
                    action='store',
                    default='',
                    dest='course',
                    help='org/num/run'),
    )


    def handle(self, *args, **options):
        self.simulate_query_iterator(options['course'])

    def get_course_qset(self, course_id):
        try:
            course = get_course(course_id)
        except ValueError:
            raise CommandError("Unknown course with id {}".format(course_id))

        qset = _get_recipient_queryset(user_id=6, to_option='all', course_id=course_id, course_location=course.location)

        return qset

    @profile
    def simulate_query_iterator(self, course_id):
        items_qset = self.get_course_qset(course_id)
        items_count = items_qset.count()
        item_list = []

        for items in _generate_items_for_subtask(items_qset, ['profile__name', 'email'], items_count, 10000, math.ceil(items_count / 10000)):
            for item in items:
                item_list.append(item)  # accumulate these items to get memory profile to report on size of accumulated list

        print(len(item_list))
