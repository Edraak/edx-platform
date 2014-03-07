# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'XBlockInfo.package_name'
        db.add_column('xblock_registry_xblockinfo', 'package_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'XBlockInfo.package_name'
        db.delete_column('xblock_registry_xblockinfo', 'package_name')


    models = {
        'xblock_registry.xblockinfo': {
            'Meta': {'ordering': "['name']", 'object_name': 'XBlockInfo'},
            'commit': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'primary_key': 'True'}),
            'package_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'repo': ('django.db.models.fields.URLField', [], {'max_length': '512', 'blank': 'True'}),
            'screenshot': ('django.db.models.fields.URLField', [], {'default': "'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png'", 'max_length': '512', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'disabled'", 'max_length': '24'}),
            'summary': ('django.db.models.fields.CharField', [], {'default': "'A building problem that uses a simulation of lincoln logs'", 'max_length': '512', 'blank': 'True'})
        }
    }

    complete_apps = ['xblock_registry']