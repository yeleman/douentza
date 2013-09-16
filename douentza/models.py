#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from picklefield.fields import PickledObjectField

from douentza._compat import implements_to_string
from douentza.utils import OPERATORS, to_jstimestamp


class IncomingManager(models.Manager):

    def get_query_set(self):
        return super(IncomingManager, self).get_query_set() \
                                           .exclude(status__in=(HotlineRequest.STATUS_GAVE_UP,
                                                                HotlineRequest.STATUS_HANDLED,
                                                                HotlineRequest.STATUS_BLACK_LIST))


class ValidatedManager(models.Manager):

    def get_query_set(self):
        return super(ValidatedManager, self).get_query_set() \
                                            .filter(status=Survey.STATUS_READY)



@implements_to_string
class HotlineRequest(models.Model):

    class Meta:
        unique_together = [('identity', 'received_on')]
        get_latest_by = "received_on"

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

    TYPES = {
        TYPE_CALL_ME: "Peux-tu me rappeler?",
        TYPE_CHARGE_ME: "Peux-tu recharger mon compte?",
        TYPE_RING: "Bip.",
        TYPE_SMS: "SMS",
        TYPE_SMS_SPAM: "SMS (SPAM)"}

    HOTLINE_TYPES = (TYPE_CALL_ME, TYPE_CHARGE_ME, TYPE_SMS, TYPE_RING)
    SMS_TYPES = (TYPE_SMS, TYPE_SMS_SPAM)

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

    objects = models.Manager()
    incoming = IncomingManager()

    def __str__(self):
        return "{event_type}-{number}-{status}".format(event_type=self.event_type,
                                                       status=self.status,
                                                       number=self.identity)

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'responded_on': to_jstimestamp(self.responded_on),
        }

    def add_busy_call(self, new_status):
        callbackattempt = CallbackAttempt(event=self, status=new_status)
        callbackattempt.save()

        if self.callbackattempts.count() >= 3:
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

    def gender(self):
        return self.SEXES.get(self.sex, self.SEX_UNKNOWN)

    def duration_delta(self):
        return datetime.timedelta(seconds=self.duration)

    def status_str(self):
        return self.STATUSES.get(self.status)

    def type_str(self):
        return self.TYPES.get(self.event_type)


@implements_to_string
class AdditionalRequest(models.Model):
    event = models.ForeignKey(HotlineRequest, related_name='additionalrequests')
    created_on = models.DateTimeField(auto_now_add=True)
    request_type = models.CharField(max_length=50,
                                    choices=HotlineRequest.TYPES.items())
    sms_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return "{event}/{type}".format(event=self.event,
                                         type=self.request_type)


@implements_to_string
class CallbackAttempt(models.Model):

    class Meta:
        get_latest_by = "created_on"

    event = models.ForeignKey(HotlineRequest, related_name='callbackattempts')
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,
                              choices=HotlineRequest.STATUSES.items())

    def __str__(self):
        return "{event}/{created_on}".format(event=self.event,
                                             created_on=self.created_on)


@implements_to_string
class HotlineUser(AbstractUser):

    def full_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username

    def __str__(self):
        return self.full_name()


@implements_to_string
class Ethnicity(models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=40, verbose_name="Nom")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Ethnicity, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


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


@implements_to_string
class Project(models.Model):
    name = models.CharField(max_length=70, verbose_name="Nom")
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


@implements_to_string
class Survey(models.Model):

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
    validated = ValidatedManager()

    def __str__(self):
        return self.title

    def to_dict(self):
        d = {'title': self.title,
             'description': self.description,
             'questions': []}
        for question in self.questions.order_by('-order', 'id'):
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


@implements_to_string
class Question(models.Model):

    class Meta:
        get_latest_by = 'order'

    TYPE_STRING = 'string'
    TYPE_BOOLEAN = 'boolean'
    TYPE_DATE = 'date'
    TYPE_INTEGER = 'int'
    TYPE_FLOAT = 'float'
    TYPE_CHOICES = 'choice'
    TYPE_TEXT = 'text'

    TYPES = {
        TYPE_STRING: "Texte court",
        TYPE_TEXT: "Texte",
        TYPE_BOOLEAN: "Vrai/Faux",
        TYPE_DATE: "Date",
        TYPE_INTEGER: "Nombre (entier)",
        TYPE_FLOAT: "Nombre (réel)",
        TYPE_CHOICES: "Liste de choix"
    }

    TYPES_CLS = {
        TYPE_STRING: forms.CharField(),
        TYPE_TEXT: forms.CharField(),
        TYPE_BOOLEAN: forms.BooleanField(),
        TYPE_DATE : forms.DateField(),
        TYPE_INTEGER: forms.IntegerField(),
        TYPE_FLOAT: forms.FloatField(),
        TYPE_CHOICES: forms.ChoiceField(),
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

    def type_str(self):
        return self.TYPES.get(self.question_type)

    def to_dict(self):
        d = {'id': self.id,
             'order': self.order,
             'label': self.label,
             'type': self.question_type,
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

    slug = models.CharField(max_length=20)
    label = models.CharField(max_length=70, verbose_name="Choix")
    question = models.ForeignKey('Question', related_name='questionchoices')

    def __str__(self):
        return "{question}-{label}".format(label=self.label,
                                           question=self.question)

    def to_dict(self):
        return {'slug': self.slug,
                'label': self.label}


@implements_to_string
class Tag(models.Model):
    slug = models.CharField(max_length=50, primary_key=True)

    def __str__(self):
        return self.slug


@implements_to_string
class BlacklistedNumber(models.Model):

    identity = models.CharField(max_length=30, unique=True)
    call_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.identity


@implements_to_string
class SurveyTaken(models.Model):

    class Meta:
        unique_together = ('survey', 'request')

    survey = models.ForeignKey('Survey', related_name='survey_takens')
    request = models.ForeignKey('HotlineRequest', related_name='survey_takens')
    taken_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.survey)

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
