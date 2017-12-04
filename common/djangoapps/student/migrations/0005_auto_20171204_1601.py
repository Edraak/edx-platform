# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.db import migrations, models


def get_meta(self):
    js_str = self.meta
    if not js_str:
        js_str = dict()
    else:
        js_str = json.loads(self.meta)

    return js_str


def track_names(apps, schema_editor):
    # We can't import the Profile and History models directly as they
    # may be a newer version than this migration expects. We use the
    # historical version.
    Profile = apps.get_model('student', 'UserProfile')
    History = apps.get_model('student', 'UserFullNameHistory')

    for profile in Profile.objects.all():
        meta = get_meta(profile)
        old_names = meta.get('old_names', [])
        for name in old_names:
            instance = History.objects.create(
                user=profile.user,
                name=name[0],
                description=name[1]
            )
            instance.created = name[2]
            instance.save()

        History.objects.create(
            user=profile.user,
            name=profile.name,
            name_en=profile.name_en,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0004_userfullnamehistory'),
    ]

    operations = [
        migrations.RunPython(track_names),
    ]
