#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from douentza.models import (HotlineRequest, Project, Ethnicity,
                             Entity, Survey, Question)
from douentza.utils import EMPTY_ENTITY

help_duration = "Durée en secondes ou sous la forme 2:30"
help_age = "L'âge en année"


class DurationField(forms.IntegerField):
    def to_python(self, value):
        if ':' in value:
            minutes, seconds = value.split(':', 1)
        else:
            minutes = 0
            seconds = value
        try:
            if not minutes:
                minutes = 0
            if not seconds:
                seconds = 0
            value = int(minutes) * 60 + int(seconds)
        except:
            raise ValidationError("Impossible de comprendre la durée",
                                  code='invalid')
        return value


class BasicInformationForm(forms.Form):

    request_id = forms.IntegerField(widget=forms.HiddenInput)
    responded_on = forms.DateTimeField(label="Date de l'appel",
                                       help_text="Format: JJ/MM/AAAA",
                                       widget=forms.SplitDateTimeWidget)

    age = forms.IntegerField(
        label="Âge", required=False,
        widget=forms.TextInput(attrs={'placeholder': help_age}))
    sex = forms.ChoiceField(label="Sexe", required=False,
                            choices=HotlineRequest.SEXES.items(),
                            widget=forms.Select)
    duration = DurationField(
        label="Durée", required=True,
        widget=forms.TextInput(attrs={'placeholder': help_duration}))
    ethnicity = forms.ChoiceField(
        label="Ethnie", required=False, widget=forms.Select)
    project = forms.ChoiceField(
        label="Projet", required=False, widget=forms.Select)

    region = forms.ChoiceField(
        label="Région", choices=[], widget=forms.Select)
    cercle = forms.CharField(
        label="Cercle", widget=forms.Select, required=False)
    commune = forms.CharField(
        label="Commune", widget=forms.Select, required=False)
    village = forms.CharField(
        label="Village", widget=forms.Select, required=False)

    def __init__(self, *args, **kwargs):
        super(BasicInformationForm, self).__init__(*args, **kwargs)

        all_ethinicty = [('#', "Inconnue")] + \
            [(e.slug, e.name) for e in Ethnicity.objects.order_by('name')]
        all_project = [('#', "Aucun")] + \
            [(p.id, p.name) for p in Project.objects.order_by('name')]
        all_region = [(EMPTY_ENTITY, "INCONNUE")] +\
            [(e.slug, e.name)
             for e in Entity.objects.filter(entity_type=Entity.TYPE_REGION)
                                    .exclude(slug__startswith='99999')] + \
            [(e.slug, e.name)
             for e in Entity.objects.filter(entity_type=Entity.TYPE_REGION)
                                    .filter(slug__startswith='99999')
                                    .order_by('name')]

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
            return HotlineRequest.objects.get(
                id=int(self.cleaned_data.get('request_id')))
        except HotlineRequest.DoesNotExist:
            raise forms.ValidationError("Évennement incorrect")

    def clean_project(self):
        project_id = self.cleaned_data.get('project')
        if project_id == '#':
            return None

        try:
            return Project.objects.get(id=int(project_id))
        except (ValueError, Project.DoesNotExist):
            return None

    def clean_ethnicity(self):
        ethnicity_slug = self.cleaned_data.get('ethnicity')
        if ethnicity_slug == '#':
            return None

        try:
            return Ethnicity.objects.get(slug=ethnicity_slug)
        except Ethnicity.DoesNotExist:
            return None

    def clean_duration(self):
        if not self.cleaned_data.get('duration'):
            raise forms.ValidationError("Durée d'appel incorrecte.")
        return self.cleaned_data.get('duration')


def get_form_property(question_dict):
    from douentza.models import Question
    from django import forms

    question_type = question_dict.get('type', Question.TYPE_STRING)

    if question_type == Question.TYPE_CHOICES:
        field = forms.ChoiceField(
            choices=[(c.get('slug'), c.get('label'))
                     for c in question_dict.get('choices')])
    elif question_type == Question.TYPE_MULTI_CHOICES:
        field = forms.MultipleChoiceField(
            choices=[(c.get('slug'), c.get('label'))
                     for c in question_dict.get('choices')])
    elif question_type == Question.TYPE_STRING:
        field = forms.CharField(max_length=250)
    elif question_type == Question.TYPE_TEXT:
        field = forms.CharField(widget=forms.Textarea)
    elif question_type == Question.TYPE_BOOLEAN:
        field = forms.NullBooleanField()
    else:
        field = Question.TYPES_CLS.get(question_type)

    field.label = question_dict.get('label')
    field.required = question_dict.get('required')
    field.widget.attrs = {'autocomplete': "off"}
    return field


class MiniSurveyForm(forms.Form):

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        super(MiniSurveyForm, self).__init__(*args, **kwargs)

        questions = survey.get('questions', [])
        if not questions:
            return

        for idx, question in enumerate(questions):
            self.fields["question_{}".format(
                question.get('id'))] = get_form_property(question)


class MiniSurveyInitForm(forms.ModelForm):

    class Meta:
        model = Survey
        fields = ['title', 'description']


class MiniSurveyAddQuestion(forms.ModelForm):

    question_choices = forms.CharField(widget=forms.Textarea,
                                       required=False,
                                       help_text="Insérez les choix ici ; "
                                                 "un par ligne.")

    class Meta:
        model = Question
        fields = ['order', 'label', 'question_type', 'required']

    def clean_question_choices(self):
        txt_choices = self.cleaned_data.get('question_choices')
        return [(slugify(choice.strip()), choice.strip())
                for choice in txt_choices.split('\n') if len(choice.strip())]


class AddProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
