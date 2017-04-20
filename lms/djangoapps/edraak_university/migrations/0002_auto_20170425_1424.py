# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_university', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UniversityIDSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_key', xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('registration_end_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('terms_and_conditions_ar', models.TextField(null=True, blank=True)),
                ('terms_and_conditions_en', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='universityid',
            name='terms_and_conditions_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='universityid',
            name='date_created',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='universityid',
            name='section_number',
            field=models.CharField(max_length=10, verbose_name='Section Number'),
        ),
        migrations.AlterField(
            model_name='universityid',
            name='university_id',
            field=models.CharField(max_length=100, verbose_name='Student University ID'),
        ),
    ]
