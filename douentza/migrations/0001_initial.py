# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HotlineEvent'
        db.create_table(u'douentza_hotlineevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identity', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('event_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('received_on', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sms_message', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('operator', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hotline_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.HotlineUser'], null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['HotlineEvent'])

        # Adding unique constraint on 'HotlineEvent', fields ['identity', 'received_on']
        db.create_unique(u'douentza_hotlineevent', ['identity', 'received_on'])

        # Adding model 'Callback'
        db.create_table(u'douentza_callback', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'callback', to=orm['douentza.HotlineEvent'])),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['Callback'])

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

        # Adding model 'HotlineResponse'
        db.create_table(u'douentza_hotlineresponse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('response_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('created_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'response', unique=True, to=orm['douentza.HotlineEvent'])),
            ('age', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(default=u'unknow', max_length=6)),
            ('duration', self.gf('django.db.models.fields.PositiveIntegerField')(max_length=4)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Entity'])),
            ('ethnicity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.Ethnicity'], null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['HotlineResponse'])

        # Adding model 'Ethnicity'
        db.create_table(u'douentza_ethnicity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal(u'douentza', ['Ethnicity'])

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
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['Project'])

        # Adding model 'Survey'
        db.create_table(u'douentza_survey', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'survey', to=orm['douentza.Project'])),
            ('reponse', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['douentza.HotlineResponse'], null=True, blank=True)),
        ))
        db.send_create_signal(u'douentza', ['Survey'])

        # Adding model 'Question'
        db.create_table(u'douentza_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('question_type', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('survey', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'questions', to=orm['douentza.Survey'])),
        ))
        db.send_create_signal(u'douentza', ['Question'])

        # Adding model 'QuestionChoice'
        db.create_table(u'douentza_questionchoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'choices', to=orm['douentza.Question'])),
        ))
        db.send_create_signal(u'douentza', ['QuestionChoice'])

        # Adding unique constraint on 'QuestionChoice', fields ['label', 'question']
        db.create_unique(u'douentza_questionchoice', ['label', 'question_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'QuestionChoice', fields ['label', 'question']
        db.delete_unique(u'douentza_questionchoice', ['label', 'question_id'])

        # Removing unique constraint on 'HotlineEvent', fields ['identity', 'received_on']
        db.delete_unique(u'douentza_hotlineevent', ['identity', 'received_on'])

        # Deleting model 'HotlineEvent'
        db.delete_table(u'douentza_hotlineevent')

        # Deleting model 'Callback'
        db.delete_table(u'douentza_callback')

        # Deleting model 'HotlineUser'
        db.delete_table(u'douentza_hotlineuser')

        # Removing M2M table for field groups on 'HotlineUser'
        db.delete_table(db.shorten_name(u'douentza_hotlineuser_groups'))

        # Removing M2M table for field user_permissions on 'HotlineUser'
        db.delete_table(db.shorten_name(u'douentza_hotlineuser_user_permissions'))

        # Deleting model 'HotlineResponse'
        db.delete_table(u'douentza_hotlineresponse')

        # Deleting model 'Ethnicity'
        db.delete_table(u'douentza_ethnicity')

        # Deleting model 'Entity'
        db.delete_table(u'douentza_entity')

        # Deleting model 'Project'
        db.delete_table(u'douentza_project')

        # Deleting model 'Survey'
        db.delete_table(u'douentza_survey')

        # Deleting model 'Question'
        db.delete_table(u'douentza_question')

        # Deleting model 'QuestionChoice'
        db.delete_table(u'douentza_questionchoice')


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
        u'douentza.callback': {
            'Meta': {'object_name': 'Callback'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'callback'", 'to': u"orm['douentza.HotlineEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
            'Meta': {'object_name': 'Ethnicity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'douentza.hotlineevent': {
            'Meta': {'unique_together': "[(u'identity', u'received_on')]", 'object_name': 'HotlineEvent'},
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'event_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'hotline_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.HotlineUser']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'operator': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'received_on': ('django.db.models.fields.DateTimeField', [], {}),
            'sms_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'douentza.hotlineresponse': {
            'Meta': {'object_name': 'HotlineResponse'},
            'age': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'created_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'ethnicity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Ethnicity']", 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'response'", 'unique': 'True', 'to': u"orm['douentza.HotlineEvent']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.Entity']"}),
            'response_date': ('django.db.models.fields.DateTimeField', [], {}),
            'sex': ('django.db.models.fields.CharField', [], {'default': "u'unknow'", 'max_length': '6'})
        },
        u'douentza.hotlineuser': {
            'Meta': {'object_name': 'HotlineUser'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'douentza.project': {
            'Meta': {'object_name': 'Project'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'})
        },
        u'douentza.question': {
            'Meta': {'object_name': 'Question'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'question_type': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'survey': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'questions'", 'to': u"orm['douentza.Survey']"})
        },
        u'douentza.questionchoice': {
            'Meta': {'unique_together': "((u'label', u'question'),)", 'object_name': 'QuestionChoice'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'choices'", 'to': u"orm['douentza.Question']"}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'douentza.survey': {
            'Meta': {'object_name': 'Survey'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'survey'", 'to': u"orm['douentza.Project']"}),
            'reponse': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['douentza.HotlineResponse']", 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['douentza']