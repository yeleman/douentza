#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.db import models
from django.contrib.auth.models import AbstractUser
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

    TYPE_CALL_ME = 'CALL_ME'
    TYPE_CHARGE_ME = 'CHARGE_ME'
    TYPE_RING = 'RING'
    TYPE_SMS_UNKNOWN = 'SMS_UNKNOWN'
    TYPE_SMS_HOTLINE = 'SMS_HOTLINE'
    TYPE_SMS_SPAM = 'SMS_SPAM'
    TYPES = ((TYPE_CALL_ME, "Peux-tu me rappeler?"),
             (TYPE_CHARGE_ME, "Peux-tu recharger mon compte?"),
             (TYPE_RING, "Bip."),
             (TYPE_SMS_UNKNOWN, "SMS à déterminer."),
             (TYPE_SMS_HOTLINE, "SMS (Hotline)."),
             (TYPE_SMS_SPAM, "SMS (SPAM)"))
    HOTLINE_TYPES = (TYPE_CALL_ME, TYPE_CHARGE_ME, TYPE_SMS_HOTLINE, TYPE_RING)
    SMS_TYPES = (TYPE_SMS_UNKNOWN, TYPE_SMS_HOTLINE, TYPE_SMS_SPAM)

    identity = models.CharField(max_length=30)
    event_type = models.CharField(max_length=50, choices=TYPES)
    received_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)
    hotline_number = models.CharField(max_length=30, null=True, blank=True)
    sms_message = models.TextField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    operator = models.CharField(max_length=50, choices=OPERATORS)
    hotline_user = models.ForeignKey('HotlineUser', null=True, blank=True)

    @property
    def archived(self):
        return self.answer.exists()

    def __unicode__(self):
        return "%(type)s/%(number)s" % {'type': self.event_type,
                                        'number': self.identity}


class HotlineUser(AbstractUser):

    phone_number = models.CharField(max_length=30, null=True, blank=True)

    def full_name(self):
        if self.get_full_name():
            return self.get_full_name()
        return self.username


class HotlineResponse(models.Model):

    class Meta:
        get_latest_by = 'response_date'

    SEX_UNKNOWN = 'U'
    SEX_MALE = 'M'
    SEX_FEMALE = 'F'
    SEXES = {
        SEX_UNKNOWN: 'Inconnu',
        SEX_MALE: "Homme",
        SEX_FEMALE: "Femme"
    }

    request = models.ForeignKey(HotlineEvent, unique=True,
                                related_name='answer')
    created_on = models.DateTimeField(auto_now_add=True)
    response_date = models.DateTimeField()
    age = models.PositiveIntegerField(null=True, blank=True)
    sex = models.CharField(max_length='1', choices=SEXES.items(),
                           default=SEX_UNKNOWN)
    duration = models.PositiveIntegerField()
    location = models.ForeignKey('Entity', null=True, blank=True)

    def __unicode__(self):
        return self.request.__unicode__()


class Entity(MPTTModel):

    TYPE_REGION = 'region'
    TYPE_CERCLE = 'cercle'
    TYPE_ARRONDISSEMENT = 'arrondissement'
    TYPE_COMMUNE = 'commune'
    TYPE_VILLAGE = 'village'

    TYPES = {
        TYPE_REGION: "Région",
        TYPE_CERCLE: "Cercle",
        TYPE_ARRONDISSEMENT: "Arrondissement",
        TYPE_COMMUNE: "Commune",
        TYPE_VILLAGE: "Village"
    }

    slug = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=30, choices=TYPES.items())
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
            return self.parent.type
        return self.parent


class Survey(models.Model):
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "{title}".format(title=self.title)


class Question(models.Model):
    TYPE_STRING = 'string'
    TYPE_BOOL = 'bool'
    TYPE_DATE = 'date'
    TYPE_INT = 'int'
    TYPE_FLOAT = 'float'
    TYPE_CHOICE = 'choice'

    TYPES = {
        TYPE_STRING: "String",
        TYPE_BOOL: "Bool",
        TYPE_DATE: "Date",
        TYPE_INT: "Int",
        TYPE_FLOAT: "Float",
        TYPE_CHOICE: "Choice"
    }

    order = models.PositiveIntegerField(verbose_name="Ordre")
    label = models.CharField(max_length=200, verbose_name='Question')
    type = models.CharField(max_length=30, choices=TYPES.items())
    survey = models.ForeignKey('Survey', related_name='questions')

    def __unicode__(self):
        return "{label}".format(label=self.label)


class Choices(models.Model):

    name = models.CharField(max_length=30, verbose_name="Nom")
    slug = models.CharField(max_length=20, primary_key=True)
    question = models.ForeignKey('Question', related_name="choices")

    def __unicode__(self):
        return "{name}/{slug}".format(name=self.name, slug=self.slug)
