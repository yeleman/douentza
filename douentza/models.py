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


ORANGE = 'O'
MALITEL = 'M'

OPERATORS = ((ORANGE, 'Orange'),
             (MALITEL, 'Malitel'))


class HotlineEvent(models.Model):

    class Meta:
        unique_together = [('identity', 'received_on')]
        get_latest_by = "received_on"

    STATUS_NEW = 'NEW'
    STATUS_NOT_RESPONDED = 'NOT_RESPONSE'
    STATUS_RESPONDED = 'RESPONDED'
    STATUS_BUSY = 'BUSY'
    STATUS = ((STATUS_NEW, "A appeler"),
             (STATUS_NOT_RESPONDED, "Ne repond pas"),
             (STATUS_RESPONDED, "Repondu"),
             (STATUS_BUSY, "Occupé"))

    TYPE_CALL_ME = 'CALL_ME'
    TYPE_CHARGE_ME = 'CHARGE_ME'
    TYPE_RING = 'RING'
    TYPE_SMS_HOTLINE = 'SMS_HOTLINE'
    TYPE_SMS_SPAM = 'SMS_SPAM'

    TYPES = ((TYPE_CALL_ME, "Peux-tu me rappeler?"),
             (TYPE_CHARGE_ME, "Peux-tu recharger mon compte?"),
             (TYPE_RING, "Bip."),
             (TYPE_SMS_HOTLINE, "SMS (Hotline)."),
             (TYPE_SMS_SPAM, "SMS (SPAM)"))
    HOTLINE_TYPES = (TYPE_CALL_ME, TYPE_CHARGE_ME, TYPE_SMS_HOTLINE, TYPE_RING)
    SMS_TYPES = (TYPE_SMS_HOTLINE, TYPE_SMS_SPAM)

    identity = models.CharField(max_length=30)
    event_type = models.CharField(max_length=50, choices=TYPES)
    status = models.CharField(max_length=50, choices=STATUS)
    received_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    sms_message = models.TextField(null=True, blank=True)
    operator = models.CharField(max_length=50, choices=OPERATORS)
    hotline_user = models.ForeignKey('HotlineUser', null=True, blank=True)

    def __unicode__(self):
        return "{event_type}/{number}/{status}".format(event_type=self.event_type,
                                                       status=self.status,
                                                       number=self.identity)

    def to_dict(self):
        return {'identity': self.identity, 'text': self.sms_message,
                'status': self.status, 'event_type': self.event_type,
                'event_id': self.id,
                'received_on': self.received_on.strftime("%d %B %Y %Hh:%Mmn"),
                'time_received_on': self.received_on.strftime("%Hh:%Mmn")}


class Callback(models.Model):
    event = models.ForeignKey(HotlineEvent, related_name='callback')
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "{event}/{created_on}".format(event=self.event.__unicode__(),
                                             created_on=self.created_on)

    def to_dict(self):
        return {'event': self.event,
                'received_on': self.received_on.strftime("%d %B %Y %Hh:%Mmn"),
                'time_received_on': self.received_on.strftime("%Hh:%Mmn")}

class HotlineUser(AbstractUser):

    def full_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username


class HotlineResponse(models.Model):

    class Meta:
        get_latest_by = 'response_date'

    SEX_UNKNOWN = 'unknow'
    SEX_MALE = 'male'
    SEX_FEMALE = 'female'
    SEXES = {
        SEX_UNKNOWN: 'Inconnu',
        SEX_MALE: "Homme",
        SEX_FEMALE: "Femme"
    }

    response_date = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(HotlineEvent, unique=True, related_name='response')
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length=6, choices=SEXES.items(),
                           default=SEX_UNKNOWN)
    duration = models.PositiveIntegerField(max_length=4,
                                           help_text="Donnez la durée en seconde")
    location = models.ForeignKey('Entity')
    ethnicity = models.ForeignKey('Ethnicity', null=True, blank=True )

    def __unicode__(self):
        return "{event}/{response_date}/{location}".format(event=self.event.__unicode__(),
                                                           response_date=self.response_date,
                                                           location=self.location)


class Ethnicity(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=40, verbose_name="Nom")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Ethnicity, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


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
        TYPE_OTHER:'Autre'
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

    def __unicode__(self):
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


class Project(models.Model):
    name = models.CharField(max_length=70, verbose_name='Nom')
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class Survey(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey('Project', related_name='survey')
    reponse = models.ForeignKey('HotlineResponse', null=True, blank=True)


    def __unicode__(self):
        return self.title


class Question(models.Model):

    class Meta:
        get_latest_by = 'order'

    TYPE_STRING = 'string'
    TYPE_BOOL = 'boolean'
    TYPE_DATE = 'date'
    TYPE_INT = 'int'
    TYPE_FLOAT = 'float'
    TYPE_CHOICE = 'choice'

    TYPES = {
        TYPE_STRING: "Chaîne",
        TYPE_BOOL: "Booléen",
        TYPE_DATE: "Date",
        TYPE_INT: "Entier",
        TYPE_FLOAT: "Réel",
        TYPE_CHOICE: "Choix"
    }

    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    label = models.CharField(max_length=200, verbose_name='Question')
    question_type = models.CharField(max_length=30, choices=TYPES.items())
    survey = models.ForeignKey('Survey', related_name='questions')

    def __unicode__(self):
        return "{survey}/{label}".format(label=self.label,
                                         survey=self.survey.__unicode__())


class QuestionChoice(models.Model):

    class Meta:
        unique_together = (('label', 'question'),)

    slug = models.CharField(max_length=20)
    label = models.CharField(max_length=70, verbose_name="Choix")
    question = models.ForeignKey('Question', related_name="choices")

    def __unicode__(self):
        return "{question}/{label}".format(label=self.label,
                                           question=self.question.__unicode__())
