"""Just using models.py to connect the signal"""
from django.db.models.signals import post_save
from courseware.models import StudentModule
from .util import log_studentmodule

post_save.connect(log_studentmodule, sender=StudentModule, dispatch_uid="bind_me_once")