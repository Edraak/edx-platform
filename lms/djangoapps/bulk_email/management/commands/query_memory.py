from optparse import make_option
from textwrap import dedent

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from courseware.courses import get_course
from bulk_email.tasks import (
    _get_num_items_for_to_option,
    _get_num_subtasks_for_to_option,
    recipient_generator,
)
from memory_profiler import profile
from instructor_task.subtasks import (
    _generate_items_for_subtask,
)
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from opaque_keys.edx.locations import SlashSeparatedCourseKey

import math

class Command(BaseCommand):
    """
    testing memory usage

    """
    def course_key_from_arg(self, arg):
        """
        Convert the command line arg into a course key
        """
        try:
            return CourseKey.from_string(arg)
        except InvalidKeyError:
            return SlashSeparatedCourseKey.from_deprecated_string(arg)

    help = dedent(__doc__).strip()

    option_list = BaseCommand.option_list + (
        make_option('--course',
                    action='store',
                    default='',
                    dest='course',
                    help='org/num/run'),
        make_option('--user_id',
                    action='store',
                    default='',
                    dest='user_id'
                    help='user_id'),
    )


    def handle(self, *args, **options):
        self.simulate_query_iterator(options['course'], options['user_id'])


    @profile
    def simulate_query_iterator(self, course_id, user_id):
        to_option = 'all'
        course_id = self.course_key_from_arg(course_id)
        user_id = user_id
        recipient_fields = ['pk', 'profile__name', 'email', 'courseenrollment__id']
        item_generator = recipient_generator(user_id, to_option, course_id, recipient_fields)
        total_num_items = _get_num_items_for_to_option(to_option, course_id, user_id)
        total_num_subtasks = _get_num_subtasks_for_to_option(to_option, course_id, user_id)

        item_list = []

        for items in _generate_items_for_subtask(item_generator, recipient_fields, total_num_items, total_num_subtasks, settings.BULK_EMAIL_EMAILS_PER_QUERY, settings.BULK_EMAIL_EMAILS_PER_TASK,):
            for item in items:
                item_list.append(item)  # accumulate these items to get memory profile to report on size of accumulated list

        print(len(item_list))