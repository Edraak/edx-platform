import time
from datetime import timedelta, datetime
from collections import deque
from django.db.models import Min

from courseware.models import StudentModuleHistory
from exploded.util import log_studentmodulehistories

SECONDS_TOLERANCE_FOR_EQ = 2
BUFFER_SIZE = 1000
DB_BATCH = 100
SLEEP_SECS = 10
START_PK = 0


class StudentModuleHistoryDeDuper(object):
    def __init__(self):
        self.buffer = deque([])
        self.num_written = 0
        ##  initialize cur_pk.  This is the pk of the last item processed
        if START_PK < 0:
            self.cur_pk = (StudentModuleHistory.objects.aggregate(min_id=Min('id'))['min_id'] - 1
                           if StudentModuleHistory.objects.all().exists()
                           else -1)
        else:
            self.cur_pk = START_PK

    def run_daemon(self, course_id=None, daemon=False):
        starttime = datetime.now()
        while True:
            self.refill_buffer(course_id)
            if len(self.buffer) == 0:
                break
            if daemon:
                if self.process_buffer(wait_until_full=True) < 0:
                    print("Buffer not full, sleeping for {} secs".format(SLEEP_SECS))
                    time.sleep(SLEEP_SECS)
            else:
                self.process_buffer(wait_until_full=False)
        print(datetime.now() - starttime)

    def refill_buffer(self, course_id):
        num_to_fetch = BUFFER_SIZE - len(self.buffer)
        #print("trying to fetch {} from {}".format(num_to_fetch, self.cur_pk))
        new_items = (StudentModuleHistory
                     .objects
                     .select_related('student_module')
                     .filter(id__gt=self.cur_pk)
                     .order_by('id'))
        if course_id:
            new_items = new_items.filter(course_id=course_id)
        new_items = new_items[:num_to_fetch]
        self.buffer.extend(new_items)
        #print("fetched")
        self.cur_pk = max([item.id for item in new_items] + [self.cur_pk])

    def process_buffer(self, wait_until_full=False):
        write_list = []
        # only do work when our buffer is full
        if wait_until_full and len(self.buffer) < BUFFER_SIZE:
            return -1
        for _ in range(DB_BATCH):
            if len(self.buffer) == 0:
                break
            head = self.buffer.popleft()
            #  scan the list manually, if dupe is found, discard and go on to the next element
            if StudentModuleHistoryDeDuper._scan_from_front(head, self.buffer):
                continue
            #  if not found, then head is good
            write_list.append(head)
            self.num_written += 1
            if self.num_written % 1000 == 0:
                print("{} entry written, studentmodulehistory.id={}".format(self.num_written, head.pk))
        log_studentmodulehistories(write_list, check_written=True)
        return len(write_list)

    @staticmethod
    def _scan_from_front(needle, haystack_list):
        for member in haystack_list:
            if StudentModuleHistoryDeDuper.compare_smh(needle, member):
                return True
            if (member.created - needle.created) > timedelta(seconds=SECONDS_TOLERANCE_FOR_EQ):
                return False
        return False

    @staticmethod
    def compare_smh(inst1, inst2):
        return (
            inst1.student_module_id == inst2.student_module_id and
            abs(inst1.created - inst2.created) <= timedelta(seconds=SECONDS_TOLERANCE_FOR_EQ)
        )