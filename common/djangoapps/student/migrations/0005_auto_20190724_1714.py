# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_auto_20190722_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='name_en',
            field=models.CharField(default=b'', max_length=255, null=True, blank=True),
        ),
    ]
