#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from douentza._compat import implements_to_string
from douentza.utils import OPERATORS


class IncomingManager(models.Manager):

    def get_query_set(self):
        return super(IncomingManager, self).get_query_set() \
                                           .exclude(status=HotlineRequest.STATUS_GAVE_UP)


@implements_to_string
class HotlineRequest(models.Model):

    class Meta:
        unique_together = [('identity', 'received_on')]
        get_latest_by = "received_on"

    SEX_UNKNOWN = 'unknow'
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

    STATUSES = {
        STATUS_NEW_REQUEST: "Nouveau",
        STATUS_NOT_ANSWERING: "Ne r√©ponds pas",
        STATUS_HANDLED: "Trait√©",
        STATUS_IS_BUSY: "Indisponible",
        STATUS_GAVE_UP: "Ne r√©ponds jamais"}

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
    identity = models.CharField(max_length=30, verbose_name="NumÈro")
    operator = models.CharField(max_length=50, choices=OPERATORS.items())
    hotline_number = models.CharField(max_length=30, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUSES.items(),
                              default=STATUS_NEW_REQUEST)
    received_on = models.DateTimeField()
    event_type = models.CharField(max_length=50, choices=TYPES.items())
    sms_message = models.TextField(null=True, blank=True)

    hotline_user = models.ForeignKey('HotlineUser', null=True, blank=True)
    responded_on = models.DateTimeField(null=True, blank=True, verbose_name="Date de l'appel")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Age")
    sex = models.CharField(max_length=6, choices=SEXES.items(),
                           default=SEX_UNKNOWN, verbose_name="Sexe")
    duration = models.PositiveIntegerField(max_length=4, null=True, blank=True,
                                           help_text="DurÈe de l'appel en seconde",
					   verbose_name="DurÈe appel")
    location = models.ForeignKey('Entity', null=True, blank=True, verbose_name="LocalitÈ")
    ethnicity = models.ForeignKey('Ethnicity', null=True, blank=True, verbose_name="…thnie")
    tags = models.ManyToManyField('Tag', null=True, blank=True, verbose_name="Tags")
    project = models.ForeignKey('Project', null=True, blank=True, verbose_name="Projet")

    objects = models.Manager()
    incoming = IncomingManager()

    def __str__(self):
        return "{event_type}-{number}-{status}".format(event_type=self.event_type,
                                                       status=self.status,
                                                       number=self.identity)

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
            AdditionalRequest.objects.create(
                event=self,
                request_type=request_type,
                sms_message=sms_message)


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

    def __str(self):
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
        TYPE_REGION: "R√©gion",
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
    name = models.CharField(max_length=70, verbose_name='Nom')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


@implements_to_string
class Survey(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(null=True, blank=True)
    event = models.ForeignKey('HotlineRequest', null=True, blank=True)


    def __str__(self):
        return self.title


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

    TYPES = {
        TYPE_STRING: "Cha√Æne",
        TYPE_BOOLEAN: "Bool√©en",
        TYPE_DATE: "Date",
        TYPE_INTEGER: "Entier",
        TYPE_FLOAT: "R√©el",
        TYPE_CHOICES: "Choix"
    }

    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    label = models.CharField(max_length=200, verbose_name='Question')
    question_type = models.CharField(max_length=30, choices=TYPES.items())
    survey = models.ForeignKey('Survey', related_name='questions')

    def __str__(self):
        return "{survey}/{label}".format(label=self.label,
                                         survey=self.survey)


@implements_to_string
class QuestionChoice(models.Model):

    class Meta:
        unique_together = (('label', 'question'),)

    slug = models.CharField(max_length=20)
    label = models.CharField(max_length=70, verbose_name="Choix")
    question = models.ForeignKey('Question', related_name="choices")

    def __str__(self):
        return "{question}-{label}".format(label=self.label,
                                           question=self.question)


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
