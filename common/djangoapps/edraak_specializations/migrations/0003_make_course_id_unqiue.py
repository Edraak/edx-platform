# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_specializations', '0002_delete_duplicate_course_ids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursespecializationinfo',
            name='course_id',
            field=models.CharField(unique=True, max_length=255, db_index=True),
        ),
    ]
