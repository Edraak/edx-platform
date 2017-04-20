# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_university', '0002_auto_20170425_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='universityid',
            name='date_created',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
