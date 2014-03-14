import json
import hashlib
from datetime import datetime
from pytz import utc
from django.conf import settings
from django.db import connections, models, transaction, DatabaseError
from django.db.utils import ConnectionDoesNotExist
from django.dispatch import receiver
from south.db import dbs
from courseware.models import StudentModule

DB_NAME = 'exploded' if settings.DATABASES.get('exploded') else 'default'
DB = dbs.get(DB_NAME)
try:
    CONN = connections['exploded']
except ConnectionDoesNotExist:
    CONN = connections['default']
TABLE_NAMES = set(CONN.introspection.table_names())


class LogModel(models.Model):
    """
    Only use this model to write to sql tables, and not to create them!
    you should only call .save() on an instance after setting the _meta.table_name manually
    """
    module_loc = models.CharField(max_length=128, db_index=True, db_column='module_loc')
    module_id = models.IntegerField(db_index=True, db_column='module_id')
    module_guid = models.CharField(max_length=64, db_index=True, db_column='module_guid')
    student_id = models.IntegerField(db_index=True, db_column='student_id')
    mkey = models.CharField(max_length=128, db_index=True, db_column='mkey')
    mtext = models.TextField(db_column='mtext', null=True)
    mnumeric = models.FloatField(db_column='mnumeric', null=True)
    mtype = models.CharField(max_length=16, db_index=True, db_column='mtype')
    orig_created = models.DateTimeField(db_index=True, db_column='orig_created')
    orig_modified = models.DateTimeField(db_index=True, db_column='orig_modified')

    class Meta:
        db_table = None


def _CREATE_INDEXES(table_name):
    DB.create_index(table_name, ['module_loc'])
    DB.create_index(table_name, ['module_id'])
    DB.create_index(table_name, ['module_guid'])
    DB.create_index(table_name, ['student_id'])
    DB.create_index(table_name, ['mkey'])
    DB.create_index(table_name, ['mtype'])
    DB.create_index(table_name, ['orig_created'])
    DB.create_index(table_name, ['orig_modified'])


def ensure_table(course_id, module_type):
    """Creates a table given the course_id and module_type.  Will do nothing if the table already exists"""
    # table names have 64 character limit
    table_name = _get_table_name(course_id, module_type)
    if table_name not in TABLE_NAMES:
        try:
            fields = LogModel._meta.fields
            DB.create_table(table_name, [(field.name, field) for field in fields])
            TABLE_NAMES.add(table_name)
            _CREATE_INDEXES(table_name)
        except DatabaseError as dbe:
            if "already exists" in dbe.message:
                TABLE_NAMES.add(table_name)


def _get_table_name(course_id, module_type):
    return u"{}__{}".format(course_id.replace(u"/", u"__"), module_type)


@transaction.commit_on_success(using=DB_NAME)
def log_studentmodule(sender, instance, **kwargs):
    """
    This is the function that logs StudentModule instances
    """
    nowstr = datetime.now(utc).isoformat("-")
    obj_guid = hashlib.sha1(nowstr + unicode(instance.id)).hexdigest()

    def write_log_kv(key, value, mtype=u'flat'):
        """uses closure in this helper fn"""
        table_name = _get_table_name(instance.course_id, instance.module_type)
        try:
            numeric = float(value)
        except:
            numeric = None
        obj = LogModel(module_loc=instance.module_state_key,
                       module_id=instance.id,
                       module_guid=obj_guid,
                       student_id=instance.student_id,
                       orig_created=instance.created,
                       orig_modified=instance.modified,
                       mkey=key[0:128],
                       mtext=value,
                       mtype=mtype,
                       mnumeric=numeric)
        obj._meta.db_table = table_name
        obj.save(using=DB_NAME)

    ensure_table(instance.course_id, instance.module_type)
    write_log_kv('max_grade', instance.max_grade)
    write_log_kv('grade', instance.grade)
    state = json.loads(instance.state)
    if type(state) != dict:
        write_log_kv('state', state)
    else:
        for (mkey, mval, mtype) in flattened_items(state):
            write_log_kv(mkey, mval, mtype)


def flattened_items(in_dict):
    """Recursively flattens the dict"""
    for top_key, top_value in in_dict.items():
        if type(top_value) == dict:
            for next_key in top_value:
                yield (top_key, next_key, u'dictkey')  # yield the top-levels keys of a dict (if the dict is a value)
            for inner_key, inner_value, inner_type in flattened_items(top_value):
                yield (top_key + "__" + inner_key, unicode(inner_value), inner_type)  # continue to unroll
        elif type(top_value) == list:
            for next_value in top_value:
                yield (top_key, next_value, u'listmember')
        else:
            yield top_key, unicode(top_value), u'flat'
