from django.contrib.auth.models import User
from django.db import models
from courseware.models import StudentModule, OfflineComputedGrade

class StudentModuleExpand(models.Model):
    """
    Expanded version of courseware's model StudentModule. This is only for
    instances of module type 'problem'. Adds attribute 'attempts' that is pulled
    out of the json in the state.
    """
    
    EXPAND_TYPES = {'problem'}

    student_module = models.ForeignKey(StudentModule, db_index=True)

    # The value mapped to 'attempts' in the json in state
    attempts = models.IntegerField(null=True, blank=True, db_index=True)

    # Values from StudentModule
    module_type = models.CharField(max_length=32, default='problem', db_index=True)
    module_state_key = models.CharField(max_length=255, db_index=True, db_column='module_id')
    student = models.ForeignKey(User, db_index=True)
    course_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = (('student', 'module_state_key', 'course_id'),)

    grade = models.FloatField(null=True, blank=True, db_index=True)
    max_grade = models.FloatField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)


class StudentGrades(models.Model):
    """
    Converted version of courseware's model OfflineComputedGrade. For a given
    instance of OfflineComptuedGrade there will be multiple instances of this.
      
    """

    course_id = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, db_index=True)

    # New Stuff
    LEVEL_TYPES = (('course','course'),
                   ('assignment_type','assignment_type'),
                   ('assignment','assignment'),
                   )
    level = models.CharField(max_length=32, choices=LEVEL_TYPES, db_index=True)

    category = models.CharField(max_length=255, db_index=True)
    percent = models.FloatField(db_index=True)
    label = models.CharField(max_length=32, db_index=True)
    detail = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = (('user', 'course_id', 'label'), )

    created = models.DateTimeField(auto_now_add=True, null=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
