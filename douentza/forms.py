#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms

from douentza.models import HotlineRequest, Project, Ethnicity, Entity
from douentza.utils import EMPTY_ENTITY

attrs = {'class': 'form-control'}

wTextInput = forms.TextInput(attrs=attrs)
wPasswordInput = forms.PasswordInput(attrs=attrs)
wHiddenInput = forms.HiddenInput(attrs=attrs)
wDateInput = forms.DateInput(attrs=attrs)
wDateTimeInput = forms.DateTimeInput(attrs=attrs)
wTimeInput = forms.TimeInput(attrs=attrs)
wTextarea = forms.Textarea(attrs=attrs)
wCheckboxInput = forms.CheckboxInput(attrs=attrs)
wSelect = forms.Select(attrs=attrs)
wNullBooleanSelect = forms.NullBooleanSelect(attrs=attrs)
wSelectMultiple = forms.SelectMultiple(attrs=attrs)
wRadioSelect = forms.RadioSelect(attrs=attrs)
wCheckboxSelectMultiple = forms.CheckboxSelectMultiple(attrs=attrs)
wFileInput = forms.FileInput(attrs=attrs)
wClearableFileInput = forms.ClearableFileInput(attrs=attrs)
wMultipleHiddenInput = forms.MultipleHiddenInput(attrs=attrs)
wSplitDateTimeWidget = forms.SplitDateTimeWidget(attrs=attrs)


class BasicInformationForm(forms.Form):

    request_id = forms.IntegerField(widget=wHiddenInput)
    responded_on = forms.DateTimeField(label="Date de l'appel",
                                       help_text="Format: JJ/MM/AAAA",
                                       widget=wSplitDateTimeWidget)

    age = forms.IntegerField(required=False, widget=wTextInput)
    sex = forms.ChoiceField(required=False,
                            choices=HotlineRequest.SEXES.items(),
                            widget=wSelect)
    duration = forms.IntegerField(widget=wTextInput)
    ethinicty = forms.ChoiceField(required=False, choices=[], widget=wSelect)
    project = forms.ChoiceField(required=False, choices=[], widget=wSelect)

    region = forms.ChoiceField(label="Région", choices=[], widget=wSelect)
    cercle = forms.CharField(label="Cercle", widget=wSelect, required=False)
    commune = forms.CharField(label="Commune", widget=wSelect, required=False)
    village = forms.CharField(label="Village", widget=wSelect, required=False)

    def __init__(self, *args, **kwargs):
        super(BasicInformationForm, self).__init__(*args, **kwargs)
        all_ethnicity = [(e.slug, e.name) for e in Ethnicity.objects.order_by('name')]
        all_project = [(p.id, p.name) for p in Project.objects.order_by('name')]
        all_region = [(EMPTY_ENTITY, "INCONNUE")] + [(e.slug, e.name)
                      for e in Entity.objects.filter(entity_type=Entity.TYPE_REGION)]

        self.fields['ethinicty'] = forms.ChoiceField(required=False,
                                                     choices=all_ethnicity,
                                                     widget=wSelect)
        self.fields['project'] = forms.ChoiceField(required=False,
                                                   choices=all_project,
                                                   widget=wSelect)
        self.fields['region'] = forms.ChoiceField(required=False,
                                                  choices=all_region,
                                                  widget=wSelect)

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
