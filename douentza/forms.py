#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms

from douentza.models import HotlineRequest, Project, Ethnicity, Entity
from douentza.utils import EMPTY_ENTITY

help_duration = "La durée est en seconde"
help_age = "Lâge en année"

class BasicInformationForm(forms.Form):

    request_id = forms.IntegerField(widget=forms.HiddenInput)
    responded_on = forms.DateTimeField(label="Date de l'appel",
                                       help_text="Format: JJ/MM/AAAA",
                                       widget=forms.SplitDateTimeWidget)

    age = forms.IntegerField(label="Âge", required=False, widget=forms.TextInput(attrs={'placeholder': help_age}))
    sex = forms.ChoiceField(label="Sexe", required=False,
                            choices=HotlineRequest.SEXES.items(),
                            widget=forms.Select)
    duration = forms.IntegerField(label="Durée", widget=forms.TextInput(attrs={'placeholder': help_duration}))
    ethnicity = forms.ChoiceField(label="Ethnie", required=False, widget=forms.Select)
    project = forms.ChoiceField(label="Projet", required=False, widget=forms.Select)

    region = forms.ChoiceField(label="Région", choices=[], widget=forms.Select)
    cercle = forms.CharField(label="Cercle", widget=forms.Select, required=False)
    commune = forms.CharField(label="Commune", widget=forms.Select, required=False)
    village = forms.CharField(label="Village", widget=forms.Select, required=False)

    def __init__(self, *args, **kwargs):
        super(BasicInformationForm, self).__init__(*args, **kwargs)

        all_ethinicty = [(e.slug, e.name) for e in Ethnicity.objects.order_by('name')]
        all_project = [(p.id, p.name) for p in Project.objects.order_by('name')]
        all_region = [(EMPTY_ENTITY, "INCONNUE")] + [(e.slug, e.name)
                      for e in Entity.objects.filter(entity_type=Entity.TYPE_REGION)]

        self.fields['ethnicity'].choices = all_ethinicty
        self.fields['project'].choices = all_project
        self.fields['region'].choices = all_region

    def clean_village(self):
            ''' Returns a Village Entity from the multiple selects '''
            is_empty = lambda l: l is None or l == EMPTY_ENTITY
            location = None
            levels = ['region', 'cercle', 'commune', 'village']
            while len(levels) and is_empty(location):
                location = self.cleaned_data.get(levels.pop()) or None

            if is_empty(location):
                return None

            try:
                return Entity.objects.get(slug=location)
            except Entity.DoesNotExist:
                raise forms.ValidationError("Localité incorrecte.")

    def clean_request_id(self):
        ''' Return a HotlineRequest from the id '''
        try:
            return HotlineRequest.objects.get(id=int(self.cleaned_data.get('request_id')))
        except HotlineRequest.DoesNotExist:
            raise forms.ValidationError("Évennement incorrect")
