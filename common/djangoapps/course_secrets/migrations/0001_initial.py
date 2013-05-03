# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CourseSecret'
        db.create_table('course_secrets_coursesecret', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('course_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True)),
        ))
        db.send_create_signal('course_secrets', ['CourseSecret'])

        # Adding unique constraint on 'CourseSecret', fields ['secret', 'course_id']
        db.create_unique('course_secrets_coursesecret', ['secret', 'course_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'CourseSecret', fields ['secret', 'course_id']
        db.delete_unique('course_secrets_coursesecret', ['secret', 'course_id'])

        # Deleting model 'CourseSecret'
        db.delete_table('course_secrets_coursesecret')


    models = {
        'course_secrets.coursesecret': {
            'Meta': {'unique_together': "(('secret', 'course_id'),)", 'object_name': 'CourseSecret'},
            'course_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['course_secrets']