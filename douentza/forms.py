#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import forms
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from douentza.models import (HotlineRequest, Project, Ethnicity,
                             Entity, Survey, Question, Cluster)
from douentza.utils import EMPTY_ENTITY, make_aware

help_duration = "Duration in seconds formatted like 2:30"
help_age = "Age in years"


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
            raise ValidationError("Unparsable duration",
                                  code='invalid')
        return value


class BasicInformationForm(forms.Form):

    request_id = forms.IntegerField(widget=forms.HiddenInput)
    responded_on = forms.SplitDateTimeField(label="Date of callback",
                                            help_text="Format: DD/MM/YYYY",
                                            input_date_formats=['%d/%m/%Y'],
                                            input_time_formats=['%H:%M:%S'],
                                            widget=forms.SplitDateTimeWidget(
                                                date_format='%d/%m/%Y',
                                                time_format='%H:%M:%S'))

    age = forms.IntegerField(
        label="Age", required=False,
        widget=forms.TextInput(attrs={'placeholder': help_age}))
    sex = forms.ChoiceField(label="Gender", required=False,
                            choices=HotlineRequest.SEXES.items(),
                            widget=forms.Select)
    duration = DurationField(
        label="Duration", required=True,
        widget=forms.TextInput(attrs={'placeholder': help_duration}))
    ethnicity = forms.ChoiceField(
        label="Ethnicity", required=False, widget=forms.Select)
    project = forms.ChoiceField(
        label="Project", required=False, widget=forms.Select)
    cluster = forms.ChoiceField(
        label="Language", required=True, widget=forms.Select)

    state = forms.ChoiceField(
        label=Entity.TYPES.get(Entity.TYPE_STATE),
        choices=[], widget=forms.Select)
    lga = forms.CharField(
        label=Entity.TYPES.get(Entity.TYPE_LGA),
        widget=forms.Select, required=False)
    ward = forms.CharField(
        label=Entity.TYPES.get(Entity.TYPE_WARD),
        widget=forms.Select, required=False)

    def __init__(self, *args, **kwargs):
        super(BasicInformationForm, self).__init__(*args, **kwargs)

        all_ethinicty = [('#', "Unknown")] + \
            [(e.slug, e.name) for e in Ethnicity.objects.order_by('name')]
        all_project = [('#', "None")] + \
            [(p.id, p.name) for p in Project.objects.order_by('name')]
        all_cluster = [(c.slug, c.name)
                       for c in Cluster.objects.order_by('name')]
        all_state = [(EMPTY_ENTITY, "UNKNOWN")] +\
            [(e.slug, e.name)
             for e in Entity.objects.filter(entity_type=Entity.TYPE_STATE)
                                    .exclude(slug__startswith='99999')] + \
            [(e.slug, e.name)
             for e in Entity.objects.filter(entity_type=Entity.TYPE_STATE)
                                    .filter(slug__startswith='99999')
                                    .order_by('name')]

        self.fields['ethnicity'].choices = all_ethinicty
        self.fields['project'].choices = all_project
        self.fields['cluster'].choices = all_cluster
        self.fields['state'].choices = all_state

    def clean_responded_on(self):
        return make_aware(self.cleaned_data['responded_on'])

    def clean_ward(self):
            ''' Returns a Ward Entity from the multiple selects '''
            is_empty = lambda l: l is None or l == EMPTY_ENTITY
            location = None
            levels = ['state', 'lga', 'ward']
            while len(levels) and is_empty(location):
                location = self.cleaned_data.get(levels.pop()) or None

            if is_empty(location):
                return None

            try:
                return Entity.objects.get(slug=location)
            except Entity.DoesNotExist:
                raise forms.ValidationError("Incorrect location.")

    def clean_request_id(self):
        ''' Return a HotlineRequest from the id '''
        try:
            return HotlineRequest.objects.get(
                id=int(self.cleaned_data.get('request_id')))
        except HotlineRequest.DoesNotExist:
            raise forms.ValidationError("Incorrect Event")

    def clean_project(self):
        project_id = self.cleaned_data.get('project')
        if project_id == '#':
            return None

        try:
            return Project.objects.get(id=int(project_id))
        except (ValueError, Project.DoesNotExist):
            return None

    def clean_cluster(self):
        return Cluster.get_or_none(self.cleaned_data.get('cluster'))

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
            raise forms.ValidationError("Incorrect call duration")
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
                                       help_text="Insert choices here ; "
                                                 "one per line.")

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
