# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('util', '0002_data__default_rate_limit_config'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseSponsor',
            fields=[
                ('organizationcourse_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='organizations.OrganizationCourse')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Course Sponsor',
                'verbose_name_plural': 'Link Course Sponsors',
            },
            bases=('organizations.organizationcourse',),
        ),
    ]
