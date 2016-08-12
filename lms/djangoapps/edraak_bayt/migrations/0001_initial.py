# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaytPublishedCertificate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(db_index=True, null=True, blank=True)),
                ('course_id', models.CharField(db_index=True, max_length=255, null=True, blank=True)),
            ],
        ),
    ]
