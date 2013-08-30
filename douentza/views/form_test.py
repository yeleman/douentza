#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render
from django import forms

from douentza.models import Question


TYPES_CLS = {
    Question.TYPE_STRING: forms.CharField(),
    Question.TYPE_BOOLEAN: forms.BooleanField(),
    Question.TYPE_DATE : forms.DateField(),
    Question.TYPE_INTEGER: forms.IntegerField(),
    Question.TYPE_FLOAT: forms.FloatField(),
    Question.TYPE_CHOICES: forms.ChoiceField(),
}

def get_form_property(question):
    question_type = question.get('type', Question.TYPE_STRING)

    if question_type == Question.TYPE_CHOICES:
        field = forms.ChoiceField(choices=question.get('choices'))
    elif question_type == Question.TYPE_STRING:
        field = forms.CharField(max_length=250)
    else:
        field = TYPES_CLS.get(question_type)
    field.label = question.get('label')
    return field


class TestForm(forms.Form):

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey')
        super(TestForm, self).__init__(*args, **kwargs)

        questions = sorted(survey.get('questions', []),
                           key=lambda x: x['order'], reverse=True)
        if not questions:
            return

        for idx, question in enumerate(questions):
            self.fields["question_{}".format(idx)] = get_form_property(question)



def tester(request):
    context = {}

    survey = {
    'questions': [
        {'order': 0,
         'label': "Quel age a tu ?",
         'type': Question.TYPE_INTEGER},
        {'order': 3,
         'label': "Comment tu 'appelles ?",
         'type': Question.TYPE_STRING},
        {'order': 2,
         'label': "Avez vous des enfants ?",
         'type': Question.TYPE_CHOICES,
         'choices': [('yes', "Oui"), ('no', "No")]},
        {'order': 0,
         'label': "Tu aimes Tuska ?",
         'type': Question.TYPE_BOOLEAN},
        ]
    }

    if request.method == "POST":
        form = TestForm(request.POST, survey=survey)
        if form.is_valid():
            print("VALID !!!!!")
            from pprint import pprint as pp ; pp(form.cleaned_data)
        else:
            print("PAS VALIDE")
    else:
        form = TestForm(survey=survey)

    context.update({"form": form})

    return render(request, "test.html", context)
