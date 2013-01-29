# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'FusionTableRowId', fields ['row_id', 'object_id', 'content_type']
        db.create_unique('djangofusiontables_fusiontablerowid', ['row_id', 'object_id', 'content_type_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FusionTableRowId', fields ['row_id', 'object_id', 'content_type']
        db.delete_unique('djangofusiontables_fusiontablerowid', ['row_id', 'object_id', 'content_type_id'])


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'djangofusiontables.fusiontableexport': {
            'Meta': {'object_name': 'FusionTableExport'},
            'django_model': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fusion_table'", 'unique': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'fusion_table_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'fusion_table_url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'djangofusiontables.fusiontablerowid': {
            'Meta': {'unique_together': "(('content_type', 'object_id', 'row_id'),)", 'object_name': 'FusionTableRowId'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'row_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['djangofusiontables']