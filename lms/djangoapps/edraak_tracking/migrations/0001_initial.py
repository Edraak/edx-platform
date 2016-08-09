# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseTrackingCode',
            fields=[
                ('course_id', models.CharField(max_length=255, unique=True, serialize=False, primary_key=True, db_index=True)),
                ('code', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CourseTrackingCodeUsage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', models.CharField(max_length=255, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='coursetrackingcodeusage',
            unique_together=set([('user', 'course_id')]),
        ),
    ]
