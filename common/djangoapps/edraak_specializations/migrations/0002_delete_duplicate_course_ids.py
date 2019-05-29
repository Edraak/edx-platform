# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def delete_duplicate_entries(apps, schema_editor):
    CourseSpecializationInfo = apps.get_model('edraak_specializations', 'CourseSpecializationInfo')

    duplicates = CourseSpecializationInfo.objects.values(
        'course_id'
    ).annotate(course_id_count=models.Count('course_id')).filter(course_id_count__gt=1)

    duplicate_objects = CourseSpecializationInfo.objects.filter(course_id__in=[item['course_id'] for item in duplicates])

    for object in duplicate_objects:
        object.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('edraak_specializations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(delete_duplicate_entries)
    ]
