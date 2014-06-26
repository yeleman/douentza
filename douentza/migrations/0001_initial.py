# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Cluster'
        db.create_table(u'douentza_cluster', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
        ))
        db.send_create_signal(u'douentza', ['Cluster'])

        # Adding model 'HotlineUser'
        db.create_table(u'douentza_hotlineuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Cluster'], null=True)),
        ))
        db.send_create_signal(u'douentza', ['HotlineUser'])

        # Adding M2M table for field groups on 'HotlineUser'
        m2m_table_name = db.shorten_name(u'douentza_hotlineuser_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hotlineuser', models.ForeignKey(orm[u'douentza.hotlineuser'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['hotlineuser_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'HotlineUser'
        m2m_table_name = db.shorten_name(u'douentza_hotlineuser_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hotlineuser', models.ForeignKey(orm[u'douentza.hotlineuser'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['hotlineuser_id', 'permission_id'])

        # Adding model 'Ethnicity'
        db.create_table(u'douentza_ethnicity', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'douentza', ['Ethnicity'])

        # Adding model 'Tag'
        db.create_table(u'douentza_tag', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
        ))
        db.send_create_signal(u'douentza', ['Tag'])

        # Adding model 'BlacklistedNumber'
        db.create_table(u'douentza_blacklistednumber', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('call_count', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'douentza', ['BlacklistedNumber'])

        # Adding model 'Entity'
        db.create_table(u'douentza_entity', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('entity_type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('parent', self.gf('mptt.fields.TreeForeignKey')(blank=True, related_name=u'children', null=True, to=orm['douentza.Entity'])),
            (u'lft', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'rght', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
            (u'level', self.gf('django.db.models.fields.PositiveIntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'douentza', ['Entity'])

        # Adding model 'Project'
        db.create_table(u'douentza_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['Project'])

        # Adding model 'HotlineRequest'
        db.create_table(u'douentza_hotlinerequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('operator', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hotline_number', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'NEW_REQUEST', max_length=50)),
            ('received_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sms_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('hotline_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.HotlineUser'], null=True, blank=True)),
            ('responded_on', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('age', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(default=u'unknown', max_length=20)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=4, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Entity'], null=True, blank=True)),
            ('ethnicity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Ethnicity'], null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Project'], null=True, blank=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Cluster'], null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['HotlineRequest'])

        # Adding unique constraint on 'HotlineRequest', fields ['identity', 'received_on']
        db.create_unique(u'douentza_hotlinerequest', ['identity', 'received_on'])

        # Adding M2M table for field tags on 'HotlineRequest'
        m2m_table_name = db.shorten_name(u'douentza_hotlinerequest_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hotlinerequest', models.ForeignKey(orm[u'douentza.hotlinerequest'], null=False)),
            ('tag', models.ForeignKey(orm[u'douentza.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['hotlinerequest_id', 'tag_id'])

        # Adding model 'AdditionalRequest'
        db.create_table(u'douentza_additionalrequest', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'additionalrequests', to=orm['douentza.HotlineRequest'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('request_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sms_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['AdditionalRequest'])

        # Adding model 'CallbackAttempt'
        db.create_table(u'douentza_callbackattempt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'callbackattempts', to=orm['douentza.HotlineRequest'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'douentza', ['CallbackAttempt'])

        # Adding model 'Survey'
        db.create_table(u'douentza_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default=u'created', max_length=50)),
        ))
        db.send_create_signal(u'douentza', ['Survey'])

        # Adding model 'Question'
        db.create_table(u'douentza_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('question_type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('required', self.gf('django.db.models.fields.BooleanField')()),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'questions', to=orm['douentza.Survey'])),
        ))
        db.send_create_signal(u'douentza', ['Question'])

        # Adding model 'QuestionChoice'
        db.create_table(u'douentza_questionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'questionchoices', to=orm['douentza.Question'])),
        ))
        db.send_create_signal(u'douentza', ['QuestionChoice'])

        # Adding unique constraint on 'QuestionChoice', fields ['slug', 'question']
        db.create_unique(u'douentza_questionchoice', ['slug', 'question_id'])

        # Adding model 'SurveyTaken'
        db.create_table(u'douentza_surveytaken', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'survey_takens', to=orm['douentza.Survey'])),
            ('request', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'survey_takens', to=orm['douentza.HotlineRequest'])),
            ('taken_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['SurveyTaken'])

        # Adding unique constraint on 'SurveyTaken', fields ['survey', 'request']
        db.create_unique(u'douentza_surveytaken', ['survey_id', 'request_id'])

        # Adding model 'SurveyTakenData'
        db.create_table(u'douentza_surveytakendata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('survey_taken', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'survey_taken_data', to=orm['douentza.SurveyTaken'])),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'survey_taken_data', to=orm['douentza.Question'])),
            ('value', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['SurveyTakenData'])

        # Adding unique constraint on 'SurveyTakenData', fields ['survey_taken', 'question']
        db.create_unique(u'douentza_surveytakendata', ['survey_taken_id', 'question_id'])

        # Adding model 'CachedData'
        db.create_table(u'douentza_cacheddata', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=75, primary_key=True)),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('data_type', self.gf('django.db.models.fields.CharField')(default=u'object', max_length=50)),
            ('value', self.gf('picklefield.fields.PickledObjectField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['CachedData'])


    def backwards(self, orm):
        # Removing unique constraint on 'SurveyTakenData', fields ['survey_taken', 'question']
        db.delete_unique(u'douentza_surveytakendata', ['survey_taken_id', 'question_id'])

        # Removing unique constraint on 'SurveyTaken', fields ['survey', 'request']
        db.delete_unique(u'douentza_surveytaken', ['survey_id', 'request_id'])

        # Removing unique constraint on 'QuestionChoice', fields ['slug', 'question']
        db.delete_unique(u'douentza_questionchoice', ['slug', 'question_id'])

        # Removing unique constraint on 'HotlineRequest', fields ['identity', 'received_on']
        db.delete_unique(u'douentza_hotlinerequest', ['identity', 'received_on'])

        # Deleting model 'Cluster'
        db.delete_table(u'douentza_cluster')

        # Deleting model 'HotlineUser'
        db.delete_table(u'douentza_hotlineuser')

        # Removing M2M table for field groups on 'HotlineUser'
        db.delete_table(db.shorten_name(u'douentza_hotlineuser_groups'))

        # Removing M2M table for field user_permissions on 'HotlineUser'
        db.delete_table(db.shorten_name(u'douentza_hotlineuser_user_permissions'))

        # Deleting model 'Ethnicity'
        db.delete_table(u'douentza_ethnicity')

        # Deleting model 'Tag'
        db.delete_table(u'douentza_tag')

        # Deleting model 'BlacklistedNumber'
        db.delete_table(u'douentza_blacklistednumber')

        # Deleting model 'Entity'
        db.delete_table(u'douentza_entity')

        # Deleting model 'Project'
        db.delete_table(u'douentza_project')

        # Deleting model 'HotlineRequest'
        db.delete_table(u'douentza_hotlinerequest')

        # Removing M2M table for field tags on 'HotlineRequest'
        db.delete_table(db.shorten_name(u'douentza_hotlinerequest_tags'))

        # Deleting model 'AdditionalRequest'
        db.delete_table(u'douentza_additionalrequest')

        # Deleting model 'CallbackAttempt'
        db.delete_table(u'douentza_callbackattempt')

        # Deleting model 'Survey'
        db.delete_table(u'douentza_survey')

        # Deleting model 'Question'
        db.delete_table(u'douentza_question')

        # Deleting model 'QuestionChoice'
        db.delete_table(u'douentza_questionchoice')

        # Deleting model 'SurveyTaken'
        db.delete_table(u'douentza_surveytaken')

        # Deleting model 'SurveyTakenData'
        db.delete_table(u'douentza_surveytakendata')

        # Deleting model 'CachedData'
        db.delete_table(u'douentza_cacheddata')


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