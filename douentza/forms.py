#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms

from douentza.models import HotlineRequest, Project, Ethnicity, Entity
from douentza.utils import EMPTY_ENTITY


class BasicInformationForm(forms.Form):

    request_id = forms.IntegerField(widget=forms.HiddenInput)
    responded_on = forms.DateTimeField(label="Date de l'appel",
                                       help_text="Format: JJ/MM/AAAA",
                                       widget=forms.SplitDateTimeWidget)

    age = forms.IntegerField(required=False)
    sex = forms.ChoiceField(required=False,
                            choices=HotlineRequest.SEXES.items())
    duration = forms.IntegerField()
    ethinicty = forms.ChoiceField(required=False, choices=[])
    project = forms.ChoiceField(required=False, choices=[])

    region = forms.ChoiceField(label="Région", choices=[])
    cercle = forms.CharField(label="Cercle", widget=forms.Select, required=False)
    commune = forms.CharField(label="Commune", widget=forms.Select, required=False)
    village = forms.CharField(label="Village", widget=forms.Select, required=False)

    def __init__(self, *args, **kwargs):
        super(BasicInformationForm, self).__init__(*args, **kwargs)
        all_ethnicity = [(e.slug, e.name) for e in Ethnicity.objects.order_by('name')]
        all_project = [(p.id, p.name) for p in Project.objects.order_by('name')]
        all_region = [(EMPTY_ENTITY, "INCONNUE")] + [(e.slug, e.name)
                      for e in Entity.objects.filter(entity_type=Entity.TYPE_REGION)]

        self.fields['ethinicty'] = forms.ChoiceField(required=False, choices=all_ethnicity)
        self.fields['project'] = forms.ChoiceField(required=False, choices=all_project)
        self.fields['region'] = forms.ChoiceField(required=False, choices=all_region)

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
