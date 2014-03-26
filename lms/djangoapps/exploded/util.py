import json as json_lib
import hashlib
from datetime import datetime
import dateutil.parser
from pytz import utc
from django.conf import settings
from django.db import connections, models, transaction, DatabaseError
from django.db.utils import ConnectionDoesNotExist
from django.dispatch import receiver
from south.db import dbs
from courseware.models import StudentModule
from jsonfield import JSONField

DB_NAME = 'exploded' if settings.DATABASES.get('exploded') else 'default'
DB = dbs.get(DB_NAME)
try:
    CONN = connections['exploded']
except ConnectionDoesNotExist:
    CONN = connections['default']
TABLE_NAMES = set(CONN.introspection.table_names())


class LogModelBase(models.Model):
    """
    Only use this model to write to sql tables, and not to create them!
    you should only call .save() on an instance after setting the _meta.table_name manually
    """
    class Meta:
        abstract = True

    module_loc = models.CharField(max_length=128, db_index=True, db_column='module_loc')
    module_id = models.IntegerField(db_index=True, db_column='module_id')
    modulehistory_id = models.IntegerField(db_index=True, db_column='modulehistory_id')
    student_id = models.IntegerField(db_index=True, db_column='student_id')
    created = models.DateTimeField(db_index=True, db_column='created')
    course_id = models.CharField(max_length=255, db_index=True, db_column='course_id')

    @classmethod
    def already_written(cls, instance):
        table_name = _get_table_name(instance.student_module.course_id, instance.student_module.module_type)
        cls._meta.db_table = table_name
        return cls.objects.using(DB_NAME).filter(modulehistory_id=instance.id).exists()


class LogModelJson(LogModelBase):
    class Meta:
        db_table = None

    grade = models.FloatField(null=True, db_index=True, db_column='grade')
    max_grade = models.FloatField(null=True, db_column='max_grade')
    json = JSONField(null=True, db_column='json')


    @classmethod
    def write_log(cls, instance, check_written=False):
        """Given a courseware.models.StudentModuleHistory instance, writes a log entry"""

        if check_written and cls.already_written(instance):
            return

        table_name = _get_table_name(instance.student_module.course_id, instance.student_module.module_type)

        try:
            state = json_lib.loads(instance.state)
        except (TypeError, ValueError):
            state = {'exception': 'failed to load state'}

        obj = cls(
            module_loc=instance.student_module.module_state_key,
            module_id=instance.student_module_id,
            modulehistory_id=instance.id,
            student_id=instance.student_module.student_id,
            created=instance.created,
            course_id=instance.student_module.course_id,
            grade=instance.grade,
            max_grade=instance.max_grade,
            json=state,
        )
        obj._meta.db_table = table_name
        obj.save(using=DB_NAME)


class ProblemLogSubTable(models.Model):
    class Meta:
        abstract = True

    problem_log_id = models.IntegerField(db_index=True, db_column='problem_log_id')
    question_id = models.CharField(max_length=128, db_index=True, db_column='question_id')


class ProblemCorrectMapLog(ProblemLogSubTable):
    class Meta:
        db_table = None
    json = JSONField(null=True, db_column='json')
    correctness = models.CharField(max_length=32, null=True, db_column='correctness')
    npoints = models.IntegerField(null=True, db_column='npoints')
    msg = models.TextField(null=True, db_column='msg')
    hint = models.TextField(null=True, db_column='hint')
    hintmode = models.CharField(max_length=32, null=True, db_column='hintmode')
    queuestate = JSONField(null=True, db_column="queuestate")

    @classmethod
    def write_log(cls, cm_dict, question_id, course_id, problem_log_id):
        """given a dict corresponding to a correct_map, log it"""
        table_name = _get_problem_subtable_name(course_id, u'correctmap')
        obj = cls(
            problem_log_id=problem_log_id,
            question_id=question_id,
            json=cm_dict,
            correctness=cm_dict.get('correctness'),
            npoints=cm_dict.get('npoints'),
            msg=cm_dict.get('msg'),
            hint=cm_dict.get('hint'),
            hintmode=cm_dict.get('hintmode'),
            queuestate=cm_dict.get('queuestate')
        )
        obj._meta.db_table = table_name
        obj.save(using=DB_NAME)


class ProblemStudentAnswersLog(ProblemLogSubTable):
    class Meta:
        db_table = None

    akey = models.CharField(null=True, max_length=128, db_index=True, db_column='akey')
    aval = models.TextField(null=True, db_column='aval')
    aval_numeric = models.FloatField(null=True, db_column='aval_numeric')

    @classmethod
    def write_log(cls, student_answer, question_id, course_id, problem_log_id):
        """given the value of a student_answer (could be flat, list, or dict) corresponding to a question, log it"""

        def _get_numeric(val):
            numeric = None
            try:
                numeric = float(val)
            except (ValueError, TypeError):
                pass
            return numeric

        table_name = _get_problem_subtable_name(course_id, u'userans')

        if type(student_answer) == dict:
            for key, value in student_answer.iteritems():
                obj = cls(
                    problem_log_id=problem_log_id,
                    question_id=question_id,
                    akey=key,
                    aval=value,
                    aval_numeric=_get_numeric(value)
                )
                obj._meta.db_table = table_name
                obj.save(using=DB_NAME)
        elif type(student_answer) == list:
            for value in student_answer:
                obj = cls(
                    problem_log_id=problem_log_id,
                    question_id=question_id,
                    akey=None,
                    aval=value,
                    aval_numeric=_get_numeric(value)
                )
                obj._meta.db_table = table_name
                obj.save(using=DB_NAME)
        else:
            obj = cls(
                problem_log_id=problem_log_id,
                question_id=question_id,
                akey=None,
                aval=student_answer,
                aval_numeric=_get_numeric(student_answer)
            )
            obj._meta.db_table = table_name
            obj.save(using=DB_NAME)


class ProblemInputStateLog(ProblemLogSubTable):
    class Meta:
        db_table = None

    json = JSONField(null=True, db_column='json')

    @classmethod
    def write_log(cls, input_state, question_id, course_id, problem_log_id):
        """given the value of a input_state corresponding to a question, log it"""
        table_name = _get_problem_subtable_name(course_id, u'inputstate')

        obj = cls(
            problem_log_id=problem_log_id,
            question_id=question_id,
            json=input_state
        )
        obj._meta.db_table = table_name
        obj.save(using=DB_NAME)


class ProblemLogModelJson(LogModelBase):
    """Problem specific log table"""
    # duplicate fields here, because multi-table inheritance doesn't work due to our hack of using the same models
    # to write different tables.
    class Meta:
        db_table = None

    grade = models.FloatField(null=True, db_index=True, db_column='grade')
    max_grade = models.FloatField(null=True, db_column='max_grade')
    json = JSONField(null=True, db_column='json')
    attempts = models.IntegerField(null=True, db_index=True, db_column='attempts')
    extended_due = models.DateTimeField(null=True, db_column='extended_due')
    done = models.BooleanField(null=True, db_index=True, db_column='done')
    seed = models.IntegerField(null=True, db_column='seed')
    time_started = models.DateTimeField(null=True, db_column='time_started')
    last_submission_time = models.DateTimeField(null=True, db_column='last_submission_time')

    sub_tables = [
        # (json_key, shortened_dbtable_name_suffix, model_class)
        ('correct_map', 'correctmap', ProblemCorrectMapLog),
        ('student_answers', 'userans', ProblemStudentAnswersLog),
        ('input_state', 'inputstate', ProblemInputStateLog),
    ]

    @classmethod
    def write_log(cls, instance, check_written=False):
        """Given a courseware.models.StudentModuleHistory instance from a problem module, writes a log entry"""
        if check_written and cls.already_written(instance):
            return

        table_name = _get_table_name(instance.student_module.course_id, u'problem')

        try:
            state = json_lib.loads(instance.state)
        except (TypeError, ValueError):
            state = {'exception': 'failed to load state'}

        extended_due = _try_parse_datetimestr(state.get('extended_due'))
        time_started = _try_parse_datetimestr(state.get('time_started'))
        last_submission_time = _try_parse_datetimestr(state.get('last_submission_time'))

        obj = cls(
            module_loc=instance.student_module.module_state_key,
            module_id=instance.student_module_id,
            modulehistory_id=instance.id,
            student_id=instance.student_module.student_id,
            created=instance.created,
            course_id=instance.student_module.course_id,
            grade=instance.grade,
            max_grade=instance.max_grade,
            json=state,
            attempts=state.get('attempts'),
            extended_due=extended_due,
            done=state.get('done'),
            seed=state.get('seed'),
            time_started=time_started,
            last_submission_time=last_submission_time,
        )
        obj._meta.db_table = table_name
        obj.save(using=DB_NAME)
        for (json_key, dbtable_suffix, subtype_model) in cls.sub_tables:
            for key, value in state.get(json_key, {}).iteritems():
                subtype_model.write_log(value, key, instance.student_module.course_id, obj.id)


def _try_parse_datetimestr(datetimestr):
    try:
        return dateutil.parser.parse(datetimestr)
    except (AttributeError, ValueError, TypeError):
        return None


def create_indexes(table_name, fields):
    for field in fields:
        if field.db_index:
            DB.create_index(table_name, [field.db_column])


def _try_create_table(model_type, table_name):
    try:
        fields = model_type._meta.fields
        DB.create_table(table_name, [(field.name, field) for field in fields])
        TABLE_NAMES.add(table_name)
        create_indexes(table_name, fields)
    except DatabaseError as dbe:
        if "already exists" in dbe.message:
            TABLE_NAMES.add(table_name)


def ensure_table(course_id, module_type):
    """Creates a table given the course_id and module_type.  Will do nothing if the table already exists"""
    # table names have 64 character limit
    table_name = _get_table_name(course_id, module_type)

    if table_name not in TABLE_NAMES:
        if module_type == u'problem':
            _try_create_table(ProblemLogModelJson, table_name)
            ensure_problem_subtables(course_id)
        else:
            _try_create_table(LogModelJson, table_name)


def ensure_problem_subtables(course_id):
    for (_, subtable_name, model_type) in ProblemLogModelJson.sub_tables:
        table_name = _get_problem_subtable_name(course_id, subtable_name)
        if table_name not in TABLE_NAMES:
            _try_create_table(model_type, table_name)


def _get_table_name(course_id, module_type):
    course_id_parts = course_id.split(u"/")
    course_id_parts = [part[0:11] for part in course_id_parts]
    return u"{}__{}".format(u"__".join(course_id_parts[0:3]), module_type[0:10]).lower()


def _get_problem_subtable_name(course_id, subtype):
    prefix = _get_table_name(course_id, u'problem')
    return u"{}__{}".format(prefix, subtype[0:10])


@transaction.commit_on_success
def log_studentmodulehistories(instance_iter):
    for instance in instance_iter:
        log_studentmodulehistory(instance)


def log_studentmodulehistory(instance, check_written=False):
    """
    This is the function that logs StudentModule instances
    """
    module_type = instance.student_module.module_type
    ensure_table(instance.student_module.course_id, module_type)
    if module_type == u'problem':
        ProblemLogModelJson.write_log(instance, check_written=check_written)
    else:
        LogModelJson.write_log(instance, check_written=check_written)


#
# class LogModel(LogModelBase):
#     mkey = models.CharField(max_length=128, db_index=True, db_column='mkey')
#     mtype = models.CharField(max_length=16, db_index=True, db_column='mtype')
#     mtext = models.TextField(null=True, db_column='mtext')
#     mnumeric = models.FloatField(null=True, db_column='mnumeric')
#
#     class Meta:
#         db_table = None
#
# @transaction.commit_on_success
# def log_studentmodulehistories(instance_iter):
#     for instance in instance_iter:
#         log_studentmodulehistory(instance)
#
#
# def log_studentmodulehistory(instance):
#     """
#     This is the function that logs StudentModule instances
#     """
#     def write_log_kv(key, value, mtype=u'flat'):
#         """uses closure in this helper fn"""
#         table_name = _get_table_name(instance.student_module.course_id, instance.student_module.module_type)
#         try:
#             numeric = float(value)
#         except:
#             numeric = None
#         obj = LogModel(module_loc=instance.student_module.module_state_key,
#                        module_id=instance.student_module_id,
#                        modulehistory_id=instance.id,
#                        student_id=instance.student_module.student_id,
#                        created=instance.created,
#                        mkey=key[0:127],
#                        mtext=value,
#                        mtype=mtype,
#                        mnumeric=numeric)
#         obj._meta.db_table = table_name
#         obj.save(using=DB_NAME)
#
#     ensure_table(instance.student_module.course_id, instance.student_module.module_type)
#     write_log_kv('max_grade', instance.max_grade)
#     write_log_kv('grade', instance.grade)
#     state = json_lib.loads(instance.state)
#     if type(state) != dict:
#         write_log_kv('state', state)
#     else:
#         for (mkey, mval, mtype) in flattened_items(state):
#             write_log_kv(mkey, mval, mtype)
#
#
# def flattened_items(in_dict):
#     """Recursively flattens the dict"""
#     for top_key, top_value in in_dict.items():
#         if type(top_value) == dict:
#             for next_key in top_value:
#                 yield (top_key, next_key, u'dictkey')  # yield the top-levels keys of a dict (if the dict is a value)
#             for inner_key, inner_value, inner_type in flattened_items(top_value):
#                 yield (top_key + "__" + inner_key, unicode(inner_value), inner_type)  # continue to unroll
#         elif type(top_value) == list:
#             for next_value in top_value:
#                 yield (top_key, next_value, u'listmember')
#         else:
#             yield top_key, unicode(top_value), u'flat'
