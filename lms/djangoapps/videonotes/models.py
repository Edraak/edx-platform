from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from pytz import UTC

# Create your models here.
class VideoNote(models.Model):
	timestamp = models.IntegerField()
	user = models.ForeignKey(User)
	course_id = models.CharField(max_length=127)
	location = models.CharField(max_length=127)
	created_at = models.DateTimeField(default=datetime.now(UTC))

	class Meta:
		ordering = ['timestamp']