from django.db import models
from courseware import models.StudentModule

class StudentModuleExpand(models.Model):
    """
    Expanded version of courseware's model StudentModule. Adds attribute
    'attempts' that is pulled out of the json in state. This is only for rows
    with type 'problem'.
    """
    
    EXPAND_TYPES = {'problem'}

    student_module = models.ForeignKey(StudentModule, db_index=True)
