# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_university', '0004_auto_20170425_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='universityidsetting',
            name='registration_end_date',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
