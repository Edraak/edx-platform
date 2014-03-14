from datetime import timedelta
from collections import deque
from django.db.models import Min

from courseware.models import StudentModuleHistory
from exploded.util import DB_NAME

SEC_TOL_FOR_EQ = 5
BUFFER = deque([])
BUFFER_SIZE = 100
MAX_WRITTEN = 100



def run_daemon():
    num_written = 0
    ##  initialize cur_pk.  This is the pk of the last item processed
    cur_pk = (StudentModuleHistory.objects.aggregate(min_id=Min('id'))['min_id'] - 1
              if StudentModuleHistory.objects.all().exists()
              else -1)

    while num_written < MAX_WRITTEN:
        cur_pk = refill_buffer(cur_pk)
        if process_buffer():
            num_written += 1
    return


def refill_buffer(cur_pk):
    num_to_fetch = BUFFER_SIZE - len(BUFFER)
    new_items = StudentModuleHistory.objects.filter(id__gt=cur_pk)[:num_to_fetch]
    BUFFER.extend(new_items)

    return max([item.id for item in new_items])


def process_buffer():
    # only do work when our buffer is full (so we have stuff to compare against)
    if len(BUFFER) < BUFFER_SIZE:
        return False
    head = BUFFER.popleft()
    #  scan the list manually
    for member in BUFFER:
        if compare_smh(head, member):
            return False
    #  if not found, then head is good
    print(head.pk)
    return True

def compare_smh(inst1, inst2):
    return (
        inst1.student_module_id == inst2.student_module_id and
        abs(inst1.created - inst2.created) < timedelta(seconds=SEC_TOL_FOR_EQ)
    )