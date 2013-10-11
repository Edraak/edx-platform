from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from pytz import UTC

# Create your models here.
class VideoNote(models.Model):
	note_text = models.TextField(blank=True)
	timestamp = models.IntegerField()
	user = models.ForeignKey(User)
	course_id = models.CharField(max_length=127)
	location = models.CharField(max_length=127)
	created_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['timestamp']