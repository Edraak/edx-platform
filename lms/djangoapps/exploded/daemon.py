from datetime import timedelta, datetime
from collections import deque
from django.db.models import Min

from courseware.models import StudentModuleHistory
from exploded.util import log_studentmodulehistories

SECONDS_TOLERANCE_FOR_EQ = 5
BUFFER_SIZE = 100
MAX_WRITTEN = 100000
DB_BATCH = 20


class StudentModuleHistoryDeDuper(object):
    def __init__(self):
        self.buffer = deque([])
        self.num_written = 0
        ##  initialize cur_pk.  This is the pk of the last item processed
        self.cur_pk = (StudentModuleHistory.objects.aggregate(min_id=Min('id'))['min_id'] - 1
                       if StudentModuleHistory.objects.all().exists()
                       else -1)

    def run_daemon(self):
        starttime = datetime.now()
        while self.num_written < MAX_WRITTEN:
            self.refill_buffer()
            retv = self.process_buffer()
            if retv:
                last = retv
        print(datetime.now() - starttime)

    def refill_buffer(self):
        num_to_fetch = BUFFER_SIZE - len(self.buffer)
        new_items = (StudentModuleHistory
                     .objects
                     .select_related('student_module')
                     .filter(id__gt=self.cur_pk)
                     [:num_to_fetch])
        self.buffer.extend(new_items)
        self.cur_pk = max([item.id for item in new_items])

    def process_buffer(self):
        # only do work when our buffer is full (so we have stuff to compare against)
        write_list = []
        if len(self.buffer) < BUFFER_SIZE:
            return None
        for _ in range(DB_BATCH):
            head = self.buffer.popleft()
            #  scan the list manually, if dupe is found, discard and go on to the next element
            if StudentModuleHistoryDeDuper._scan_from_front(head, self.buffer):
                continue
            #  if not found, then head is good
            write_list.append(head)
            self.num_written += 1
            if self.num_written % 1000 == 0:
                print("{} entry written, studentmodulehistory.id={}".format(self.num_written, head.pk))
            if self.num_written >= MAX_WRITTEN:
                break
        log_studentmodulehistories(write_list)
        return head.pk

    @staticmethod
    def _scan_from_front(needle, haystack_list):
        for member in haystack_list:
            if StudentModuleHistoryDeDuper.compare_smh(needle, member):
                return True
        return False

    @staticmethod
    def compare_smh(inst1, inst2):
        return (
            inst1.student_module_id == inst2.student_module_id and
            abs(inst1.created - inst2.created) < timedelta(seconds=SECONDS_TOLERANCE_FOR_EQ)
        )