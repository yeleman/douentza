# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'HotlineRequest.email'
        db.add_column(u'douentza_hotlinerequest', 'email',
                      self.gf('django.db.models.fields.EmailField')(max_length=250, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'HotlineRequest.email'
        db.delete_column(u'douentza_hotlinerequest', 'email')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'douentza.additionalrequest': {
            'Meta': {'ordering': "(u'-created_on', u'-id')", 'object_name': 'AdditionalRequest'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'additionalrequests'", 'to': u"orm['douentza.HotlineRequest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sms_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'douentza.blacklistednumber': {
            'Meta': {'object_name': 'BlacklistedNumber'},
            'call_count': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'douentza.cacheddata': {
            'Meta': {'object_name': 'CachedData'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.CharField', [], {'default': "u'object'", 'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '75', 'primary_key': 'True'}),
            'value': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'})
        },
        u'douentza.callbackattempt': {
            'Meta': {'ordering': "(u'-created_on', u'-id')", 'object_name': 'CallbackAttempt'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'callbackattempts'", 'to': u"orm['douentza.HotlineRequest']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'douentza.cluster': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Cluster'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'primary_key': 'True'})
        },
        u'douentza.entity': {
            'Meta': {'object_name': 'Entity'},
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            u'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            u'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('mptt.fields.TreeForeignKey', [], {'blank': 'True', 'related_name': "u'children'", 'null': 'True', 'to': u"orm['douentza.Entity']"}),
            u'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20', 'primary_key': 'True'}),
            u'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        u'douentza.ethnicity': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Ethnicity'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'primary_key': 'True'})
        },
        u'douentza.hotlinerequest': {
            'Meta': {'ordering': "(u'received_on',)", 'unique_together': "[(u'identity', u'received_on')]", 'object_name': 'HotlineRequest'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Cluster']", 'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'ethnicity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Ethnicity']", 'null': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hotline_number': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'hotline_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.HotlineUser']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Entity']", 'null': 'True', 'blank': 'True'}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Project']", 'null': 'True', 'blank': 'True'}),
            'received_on': ('django.db.models.fields.DateTimeField', [], {}),
            'responded_on': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "u'unknown'", 'max_length': '20'}),
            'sms_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'NEW_REQUEST'", 'max_length': '50'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "u'requests'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['douentza.Tag']"})
        },
        u'douentza.hotlineuser': {
            'Meta': {'object_name': 'HotlineUser'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Cluster']", 'null': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'douentza.project': {
            'Meta': {'ordering': "(u'name',)", 'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'})
        },
        u'douentza.question': {
            'Meta': {'ordering': "(u'-order',)", 'object_name': 'Question'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'question_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'required': ('django.db.models.fields.BooleanField', [], {}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'questions'", 'to': u"orm['douentza.Survey']"})
        },
        u'douentza.questionchoice': {
            'Meta': {'ordering': "(u'id',)", 'unique_together': "((u'slug', u'question'),)", 'object_name': 'QuestionChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'questionchoices'", 'to': u"orm['douentza.Question']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'douentza.survey': {
            'Meta': {'ordering': "(u'id',)", 'object_name': 'Survey'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "u'created'", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'douentza.surveytaken': {
            'Meta': {'ordering': "(u'-taken_on',)", 'unique_together': "((u'survey', u'request'),)", 'object_name': 'SurveyTaken'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'request': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'survey_takens'", 'to': u"orm['douentza.HotlineRequest']"}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'survey_takens'", 'to': u"orm['douentza.Survey']"}),
            'taken_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'douentza.surveytakendata': {
            'Meta': {'unique_together': "((u'survey_taken', u'question'),)", 'object_name': 'SurveyTakenData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'survey_taken_data'", 'to': u"orm['douentza.Question']"}),
            'survey_taken': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'survey_taken_data'", 'to': u"orm['douentza.SurveyTaken']"}),
            'value': ('picklefield.fields.PickledObjectField', [], {'null': 'True', 'blank': 'True'})
        },
        u'douentza.tag': {
            'Meta': {'ordering': "(u'slug',)", 'object_name': 'Tag'},
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'})
        }
    }

    complete_apps = ['douentza']