# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'XBlockInfo'
        db.create_table('xblock_registry_xblockinfo', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=24, primary_key=True)),
            ('state', self.gf('django.db.models.fields.CharField')(default='disabled', max_length=24)),
            ('screenshot', self.gf('django.db.models.fields.URLField')(default='http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png', max_length=512, blank=True)),
            ('summary', self.gf('django.db.models.fields.CharField')(default='A building problem that uses a simulation of lincoln logs', max_length=512, blank=True)),
        ))
        db.send_create_signal('xblock_registry', ['XBlockInfo'])


    def backwards(self, orm):
        # Deleting model 'XBlockInfo'
        db.delete_table('xblock_registry_xblockinfo')


    models = {
        'xblock_registry.xblockinfo': {
            'Meta': {'ordering': "['name']", 'object_name': 'XBlockInfo'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '24', 'primary_key': 'True'}),
            'screenshot': ('django.db.models.fields.URLField', [], {'default': "'http://vikparuchuri.github.io/boston-python-ml/assets/img/multiple_choice_problem.png'", 'max_length': '512', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'disabled'", 'max_length': '24'}),
            'summary': ('django.db.models.fields.CharField', [], {'default': "'A building problem that uses a simulation of lincoln logs'", 'max_length': '512', 'blank': 'True'})
        }
    }

    complete_apps = ['xblock_registry']