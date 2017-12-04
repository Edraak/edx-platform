# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('student', '0003_auto_20171126_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFullNameHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('english_name', models.CharField(max_length=255, null=True, blank=True)),
                ('name', models.CharField(max_length=255, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
