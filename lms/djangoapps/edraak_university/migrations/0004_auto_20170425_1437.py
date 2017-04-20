# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_university', '0003_auto_20170425_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='universityid',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='universityidsetting',
            name='registration_end_date',
            field=models.DateTimeField(default=None),
        ),
    ]
