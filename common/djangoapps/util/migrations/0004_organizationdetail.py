# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('util', '0003_coursesponsor'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizationDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_en', models.CharField(max_length=255, db_index=True)),
                ('short_name_en', models.CharField(help_text='Please do not use spaces or special characters. Only allowed special characters are period (.), hyphen (-) and underscore (_).', max_length=255, verbose_name=b'English Short Name', db_index=True)),
                ('name_ar', models.CharField(max_length=255, db_index=True)),
                ('short_name_ar', models.CharField(help_text='Please do not use spaces or special characters. Only allowed special characters are period (.), hyphen (-) and underscore (_).', max_length=255, verbose_name=b'Arabic Short Name', db_index=True)),
                ('organization', models.OneToOneField(to='organizations.Organization')),
            ],
        ),
    ]