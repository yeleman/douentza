#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime
import json

from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from picklefield.fields import PickledObjectField

from py3compat import implements_to_string
from douentza.utils import OPERATORS, to_jstimestamp


@implements_to_string
class Cluster(models.Model):

    class Meta:
        ordering = ('name', )

    slug = models.SlugField(max_length=200, primary_key=True)
    name = models.CharField(max_length=70, verbose_name="Nom", unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None


@implements_to_string
class HotlineUser(AbstractUser):

    cluster = models.ForeignKey('Cluster', null=True)

    def full_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username

    def __str__(self):
        return self.full_name()

    @classmethod
    def get_or_none(cls, username):
        try:
            return cls.objects.get(username=username)
        except cls.DoesNotExist:
            return None


@implements_to_string
class Ethnicity(models.Model):

    class Meta:
        ordering = ('name', )

    slug = models.SlugField(max_length=200, primary_key=True)
    name = models.CharField(max_length=40, verbose_name="Nom")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Ethnicity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None


@implements_to_string
class Tag(models.Model):

    class Meta:
        ordering = ('slug', )

    slug = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.slug

    def to_dict(self):
        data = {'slug': self.slug}
        return data

    @classmethod
    def get_or_create(cls, text):
        try:
            tag = cls.objects.get(slug=text)
        except cls.DoesNotExist:
            tag = cls.objects.create(slug=text)
        return tag

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None


@implements_to_string
class BlacklistedNumber(models.Model):

    identity = models.CharField(max_length=30, unique=True)
    call_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.identity

    @classmethod
    def add_to_identy(cls, identity):
        try:
            bln = cls.objects.get(identity=identity)
            bln.call_count += 1
            bln.save()
        except cls.DoesNotExist:
            bln = cls.objects.create(identity=identity, call_count=1)

    @classmethod
    def get_or_none(cls, identity):
        try:
            return cls.objects.get(identity=identity)
        except cls.DoesNotExist:
            return None


@implements_to_string
class Entity(MPTTModel):

    TYPE_REGION = 'region'
    TYPE_CERCLE = 'cercle'
    TYPE_ARRONDISSEMENT = 'arrondissement'
    TYPE_COMMUNE = 'commune'
    TYPE_VILLAGE = 'village'
    TYPE_OTHER = 'autre'

    TYPES = {
        TYPE_REGION: "Région",
        TYPE_CERCLE: "Cercle",
        TYPE_ARRONDISSEMENT: "Arrondissement",
        TYPE_COMMUNE: "Commune",
        TYPE_VILLAGE: "Village",
        TYPE_OTHER: 'Autre',
    }

    slug = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=30, choices=TYPES.items())
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name="Parent")

    objects = TreeManager()

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None

    def get_ancestor_of(self, etype):
        if self.entity_type == etype:
            return self
        try:
            return [e for e in self.get_ancestors() if e.entity_type == etype][-1]
        except IndexError:
            return None

    def get_village(self):
        return self.get_ancestor_of('village')

    def get_commune(self):
        return self.get_ancestor_of('commune')

    def get_cercle(self):
        return self.get_ancestor_of('cercle')

    def get_region(self):
        return self.get_ancestor_of('region')

    def get_arrondissement(self):
        return self.get_ancestor_of('arrondissement')

    def get_autre(self):
        return self.get_ancestor_of('autre')

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return "{name}/{parent}".format(name=self.display_name(),
                                            parent=self.parent.display_name())
        return self.display_name()

    def parent_level(self):
        if self.parent:
            return self.parent.entity_type
        return self.parent

    def get_geopoint(self):
        if self.latitude and self.longitude:
            return "{lon}, {lat}".format(lon=self.longitude, lat=self.latitude)

    @property
    def geometry(self):
        return None

    @property
    def geojson(self):
        if not self.geometry:
            if self.latitude and self.longitude:
                return {"type": "Point",
                        "coordinates": [self.longitude, self.latitude]}
            return {}
        return json.loads(self.geometry)

    @property
    def geojson_feature(self):
        feature = {
            "type": "Feature",
            "properties": self.to_dict()
        }
        if self.geojson:
            feature.update({"geometry": self.geojson})
        return feature

    def display_code_name(self):
        return "{name} ({code})".format(code=self.slug,
                                        name=self.display_name())

    def display_typed_name(self):
        return "{type} de {name}".format(type=self.TYPES.get(self.entity_type), name=self.name)

    def to_dict(self):
        return {'slug': self.slug,
                'name': self.name,
                'display_typed_name': self.display_typed_name(),
                'display_code_name': self.display_code_name(),
                'display_full_name': self.display_full_name(),
                'type': self.entity_type,
                'parent': getattr(self.parent, 'slug', None),
                'latitude': self.latitude,
                'longitude': self.longitude}


@implements_to_string
class Project(models.Model):

    class Meta:
        ordering = ('name', )

    name = models.CharField(max_length=70, verbose_name="Nom", unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def get_or_none(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None


class IncomingManager(models.Manager):

    def get_query_set(self):
        return super(IncomingManager, self).get_query_set() \
                                           .exclude(status__in=(HotlineRequest.STATUS_GAVE_UP,
                                                                HotlineRequest.STATUS_HANDLED,
                                                                HotlineRequest.STATUS_BLACK_LIST))


class DoneManager(models.Manager):

    def get_query_set(self):
        return super(DoneManager, self).get_query_set() \
                                          .filter(status__in=HotlineRequest.DONE_STATUSES)


class AllManager(models.Manager):

    def get_query_set(self):
        return super(AllManager, self).get_query_set() \
                                          .exclude(status=Survey.STATUS_CREATED)

class ReadyManager(models.Manager):

    def get_query_set(self):
        return super(ReadyManager, self).get_query_set() \
                                        .filter(status=Survey.STATUS_READY)


@implements_to_string
class HotlineRequest(models.Model):

    class Meta:
        unique_together = [('identity', 'received_on')]
        get_latest_by = "received_on"
        ordering = ('received_on', )

    SEX_UNKNOWN = 'unknown'
    SEX_MALE = 'male'
    SEX_FEMALE = 'female'
    SEXES = {
        SEX_UNKNOWN: 'Inconnu',
        SEX_MALE: "Homme",
        SEX_FEMALE: "Femme"
    }

    STATUS_NEW_REQUEST = 'NEW_REQUEST'
    STATUS_NOT_ANSWERING = 'NOT_ANSWERING'
    STATUS_HANDLED = 'HANDLED'
    STATUS_IS_BUSY = 'IS_BUSY'
    STATUS_GAVE_UP = 'GAVE_UP'
    STATUS_BLACK_LIST = 'BLACK_LIST'

    STATUSES = {
        STATUS_NEW_REQUEST: "Nouveau",
        STATUS_NOT_ANSWERING: "Ne réponds pas",
        STATUS_HANDLED: "Traité",
        STATUS_IS_BUSY: "Indisponible",
        STATUS_BLACK_LIST: "Liste noire",
        STATUS_GAVE_UP: "Ne réponds jamais"}

    TYPE_CALL_ME = 'CALL_ME'
    TYPE_CHARGE_ME = 'CHARGE_ME'
    TYPE_RING = 'RING'
    TYPE_SMS = 'SMS'
    TYPE_SMS_SPAM = 'SMS_SPAM'
    TYPE_WEB = 'WEB'

    TYPES = {
        TYPE_CALL_ME: "Rappele moi",
        TYPE_CHARGE_ME: "Recharges mon compte",
        TYPE_RING: "Bip.",
        TYPE_SMS: "SMS",
        TYPE_WEB: "Web",
        TYPE_SMS_SPAM: "SMS (SPAM)"}

    HOTLINE_TYPES = (TYPE_CALL_ME, TYPE_CHARGE_ME, TYPE_SMS, TYPE_RING)
    SMS_TYPES = (TYPE_SMS, TYPE_SMS_SPAM)
    DONE_STATUSES = (STATUS_GAVE_UP, STATUS_HANDLED)

    created_on = models.DateTimeField(auto_now_add=True)
    identity = models.CharField(max_length=30, verbose_name="Numéro")
    operator = models.CharField(max_length=50, choices=OPERATORS.items())
    hotline_number = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUSES.items(),
                              default=STATUS_NEW_REQUEST)
    received_on = models.DateTimeField()
    event_type = models.CharField(max_length=50, choices=TYPES.items())
    sms_message = models.TextField(null=True, blank=True)
    hotline_user = models.ForeignKey('HotlineUser', null=True, blank=True)
    responded_on = models.DateTimeField(null=True, blank=True,
                                        verbose_name="Date de l'appel")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    sex = models.CharField(max_length=20, choices=SEXES.items(),
                           default=SEX_UNKNOWN, verbose_name="Sexe")
    duration = models.PositiveIntegerField(max_length=4, null=True, blank=True,
                                           help_text="Durée de l'appel en seconde",
                                           verbose_name="Durée appel")
    location = models.ForeignKey('Entity', null=True, blank=True, verbose_name="Localité")
    ethnicity = models.ForeignKey('Ethnicity', null=True, blank=True, verbose_name="Éthnie")
    tags = models.ManyToManyField('Tag', null=True, blank=True, verbose_name="Tags", related_name='requests')
    project = models.ForeignKey('Project', null=True, blank=True, verbose_name="Projet")
    cluster = models.ForeignKey('Cluster', null=True, blank=True)
    email = models.EmailField(max_length=250, verbose_name="E-mail", null=True, blank=True)

    objects = models.Manager()
    incoming = IncomingManager()
    done = DoneManager()

    def __str__(self):
        return "{event_type}-{number}-{status}".format(event_type=self.event_type,
                                                       status=self.status,
                                                       number=self.identity)

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None

    @property
    def request_type(self):
        return self.event_type

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'responded_on': to_jstimestamp(self.responded_on),
        }

    def add_busy_call(self, new_status):
        callbackattempt = CallbackAttempt(event=self, status=new_status)
        callbackattempt.save()

        if self.callbackattempts.exclude(status=self.STATUS_BLACK_LIST).count() >= 3:
            self.status = HotlineRequest.STATUS_GAVE_UP
        else:
            self.status = new_status
        self.save()

    def add_additional_request(self, request_type, sms_message=None):
        if self.status != HotlineRequest.STATUS_HANDLED:
            AdditionalRequest.objects.create(event=self,
                                             request_type=request_type,
                                             sms_message=sms_message)

    def previous_requests(self):
        return HotlineRequest.objects \
            .filter(identity=self.identity,
                    status=HotlineRequest.STATUS_HANDLED) \
            .exclude(id=self.id)

    def add_cluster(self, cluster_slug):
        self.cluster = Cluster.objects.get(slug=cluster_slug)
        self.save()

    def gender(self):
        return self.SEXES.get(self.sex)

    def operator_str(self):
        return OPERATORS.get(self.operator)

    def duration_delta(self):
        return datetime.timedelta(seconds=self.duration)

    def status_str(self):
        return self.STATUSES.get(self.status)

    def type_str(self):
        return self.TYPES.get(self.event_type)

    def all_events(self, reverse=False):
        events = [self] + list(self.additionalrequests.all()) + list(self.callbackattempts.all())
        return sorted(events, key=lambda e: e.received_on, reverse=reverse)

    def previous_status(self, but_type=STATUS_BLACK_LIST):
        events = self.all_events()
        while len(events):
            last = events.pop()
            if last.event_type != but_type:
                return last.event_type
        return self.STATUS_NEW_REQUEST


@implements_to_string
class AdditionalRequest(models.Model):

    class Meta:
        ordering = ('-created_on', '-id')

    event = models.ForeignKey(HotlineRequest, related_name='additionalrequests')
    created_on = models.DateTimeField(auto_now_add=True)
    request_type = models.CharField(max_length=50,
                                    choices=HotlineRequest.TYPES.items())
    sms_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{event}/{type}".format(event=self.event,
                                         type=self.request_type)

    def type_str(self):
        return HotlineRequest.TYPES.get(self.request_type)

    @property
    def received_on(self):
        return self.created_on

    @property
    def event_type(self):
        return self.request_type

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None



@implements_to_string
class CallbackAttempt(models.Model):

    class Meta:
        get_latest_by = "created_on"
        ordering = ('-created_on', '-id')

    event = models.ForeignKey(HotlineRequest, related_name='callbackattempts')
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,
                              choices=HotlineRequest.STATUSES.items())

    def __str__(self):
        return "{event}/{created_on}".format(event=self.event,
                                             created_on=self.created_on)

    def status_str(self):
        return HotlineRequest.STATUSES.get(self.status)

    @property
    def received_on(self):
        return self.created_on

    @property
    def event_type(self):
        return self.status

    def type_str(self):
        return HotlineRequest.STATUSES.get(self.status)

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None


@implements_to_string
class Survey(models.Model):

    class Meta:
        ordering = ('id', )

    STATUS_CREATED = 'created'
    STATUS_READY = 'ready'
    STATUS_DISABLED = 'disabled'

    STATUSES = {
        STATUS_CREATED: "Commencé",
        STATUS_READY: "Utilisable",
        STATUS_DISABLED: "Désactivé"
    }

    title = models.CharField(max_length=200,
                             verbose_name="Titre",
                             help_text="Nom du formulaire")
    description = models.TextField(null=True,
                                   blank=True,
                                   verbose_name="Description")
    status = models.CharField(choices=STATUSES.items(),
                              default=STATUS_CREATED,
                              max_length=50)

    objects = models.Manager()
    validated = AllManager()
    ready = ReadyManager()

    def __str__(self):
        return self.title

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None


    def to_dict(self):
        d = {'title': self.title,
             'description': self.description,
             'questions': []}
        for question in self.questions.order_by('order', '-id'):
            d['questions'].append(question.to_dict())
        return d

    @classmethod
    def availables(cls, request):
        return cls.validated.exclude(id__in=[st.id for st in request.survey_takens.all()]).order_by('id')

    def available_for(self, request):
        return not request.survey_takens.filter(survey__id=self.id).count()

    def taken(self, request):
        return request.survey_takens.get(survey__id=self.id)

    def status_str(self):
        return self.STATUSES.get(self.status, self.STATUS_CREATED)

    @property
    def cache_file_slug(self):
        return 'ms_file_{id}'.format(id=self.id)

    @property
    def cache_slug(self):
        return 'ms_data_{id}'.format(id=self.id)

    @property
    def meta_cache_slug(self):
        return 'ms_meta_data_{id}'.format(id=self.id)


@implements_to_string
class Question(models.Model):

    class Meta:
        get_latest_by = 'order'
        ordering = ('-order', )

    TYPE_STRING = 'string'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_INTEGER = 'int'
    TYPE_FLOAT = 'float'
    TYPE_CHOICES = 'choice'
    TYPE_MULTI_CHOICES = 'multi_choice'
    TYPE_TEXT = 'text'

    TYPES = {
        TYPE_STRING: "Texte court",
        TYPE_TEXT: "Texte",
        TYPE_BOOLEAN: "Vrai/Faux",
        TYPE_DATE: "Date",
        TYPE_INTEGER: "Nombre (entier)",
        TYPE_FLOAT: "Nombre (réel)",
        TYPE_CHOICES: "Liste de choix",
        TYPE_MULTI_CHOICES: "Liste de choix multiples"
    }

    TYPES_CLS = {
        TYPE_STRING: forms.CharField(),
        TYPE_TEXT: forms.CharField(),
        TYPE_BOOLEAN: forms.BooleanField(),
        TYPE_DATE: forms.DateField(),
        TYPE_INTEGER: forms.IntegerField(),
        TYPE_FLOAT: forms.FloatField(),
        TYPE_CHOICES: forms.ChoiceField(),
        TYPE_CHOICES: forms.MultipleChoiceField(),
    }

    order = models.PositiveIntegerField(default=0,
        verbose_name="Ordre",
        help_text="Ordre d'apparition. Le plus élévé en premier. "
                  "0 égal aucune priorité particulière (ordre d'ajout)")
    label = models.CharField(max_length=200,
                             verbose_name="Question",
                             help_text="Libellé de la question")
    question_type = models.CharField(max_length=30, choices=TYPES.items())
    required = models.BooleanField(verbose_name="Réponse requise")
    survey = models.ForeignKey('Survey', related_name='questions')

    def __str__(self):
        return "{survey}/{label}".format(label=self.label,
                                         survey=self.survey)

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None


    def type_str(self):
        return self.TYPES.get(self.question_type)

    def to_dict(self):
        d = {'id': self.id,
             'order': self.order,
             'label': self.label,
             'type': self.question_type,
             'has_choices': self.question_type in (self.TYPE_CHOICES, self.TYPE_MULTI_CHOICES),
             'type_str': self.type_str(),
             'required': self.required,
             'choices': []}
        for choice in self.questionchoices.order_by('id'):
            d['choices'].append(choice.to_dict())
        return d


@implements_to_string
class QuestionChoice(models.Model):

    class Meta:
        unique_together = (('slug', 'question'),)
        ordering = ('id', )

    slug = models.CharField(max_length=20)
    label = models.CharField(max_length=70, verbose_name="Choix")
    question = models.ForeignKey('Question', related_name='questionchoices')

    def __str__(self):
        return "{question}-{label}".format(label=self.label,
                                           question=self.question)

    def to_dict(self):
        return {'slug': self.slug,
                'label': self.label}

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None


@implements_to_string
class SurveyTaken(models.Model):

    class Meta:
        unique_together = ('survey', 'request')
        ordering = ('-taken_on', )

    survey = models.ForeignKey('Survey', related_name='survey_takens')
    request = models.ForeignKey('HotlineRequest', related_name='survey_takens')
    taken_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.survey)

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None

    def data_for(self, question):
        try:
            return SurveyTakenData.objects.get(survey_taken=self,
                                               question=question).value
        except SurveyTakenData.DoesNotExist:
            return None

    def to_dict(self):
        data = {'taken_on': self.taken_on,
                'request': self.request,
                'survey': self.survey,
                'questions': []}
        for question in self.survey.questions.order_by('-order', 'id'):
            question_data = question.to_dict()
            question_data.update({'value': self.data_for(question)})
            data['questions'].append(question_data)
        return data


@implements_to_string
class SurveyTakenData(models.Model):

    class Meta:
        unique_together = ('survey_taken', 'question')

    survey_taken = models.ForeignKey('SurveyTaken', related_name='survey_taken_data')
    question = models.ForeignKey('Question', related_name='survey_taken_data')
    value = PickledObjectField(null=True, blank=True)

    def __str__(self):
        return str(self.value)

    @classmethod
    def get_or_none(cls, ident):
        try:
            return cls.objects.get(id=ident)
        except cls.DoesNotExist:
            return None


@implements_to_string
class CachedData(models.Model):

    TYPE_OBJECT = 'object'
    TYPE_FILE = 'file'
    TYPES = {
        TYPE_OBJECT: "Objet",
        TYPE_FILE: "Fichier"
    }

    slug = models.CharField(max_length=75, primary_key=True)
    created_on = models.DateTimeField(auto_now_add=True)
    data_type = models.CharField(choices=TYPES.items(),
                                 default=TYPE_OBJECT, max_length=50)
    value = PickledObjectField(null=True, blank=True)

    def __str__(self):
        return self.slug

    @classmethod
    def get_or_fallback(cls, slug, fallback=None):
        try:
            return cls.objects.get(slug=slug).value
        except cls.DoesNotExist:
            raise
            return fallback

    @classmethod
    def get_or_none(cls, slug):
        try:
            return cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            return None
