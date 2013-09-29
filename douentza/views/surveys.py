#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from douentza.models import (Survey, HotlineRequest, Question,
                             SurveyTaken, SurveyTakenData)
from douentza.forms import MiniSurveyForm
from douentza.utils import get_default_context


@login_required()
def survey_form(request, survey_id, request_id):
    context = get_default_context(page='mini_survey_form')

    def terminate_survey(error=False, survey_taken=None):
        context.update({'error': error})
        if survey_taken is not None and not survey_taken.survey_taken_data.count():
            survey_taken.delete()
        return render(request, "modal_over.html", context)

    try:
        survey = get_object_or_404(Survey, id=int(survey_id))
        event = get_object_or_404(HotlineRequest, id=int(request_id))
    except ValueError:
        raise Http404

    if request.method == "POST":
        form = MiniSurveyForm(request.POST, survey=survey.to_dict())
        if form.is_valid():
            # create SurveyTaken
            try:
                survey_taken = SurveyTaken.objects.create(survey=survey,
                                                          request=event)
            except:
                return terminate_survey(True)

            # loop on question
            for question_name, question_data in form.cleaned_data.items():
                try:
                    question = Question.objects.get(id=int(question_name.split('_')[-1]))
                except:
                    return terminate_survey(True, survey_taken=survey_taken)

                try:
                    SurveyTakenData.objects.create(survey_taken=survey_taken,
                                                   question=question,
                                                   value=question_data)
                except:
                    return terminate_survey(True, survey_taken=survey_taken)

            return terminate_survey()
        else:
            pass
    else:
        form = MiniSurveyForm(survey=survey.to_dict())

    context.update({'form': form,
                    'survey': survey,
                    'request': event})

    return render(request, "mini_survey.html", context)


@login_required()
def survey_data(request, survey_id, request_id):
    context = get_default_context(page='mini_survey_data')

    try:
        survey = get_object_or_404(Survey, id=int(survey_id))
        event = get_object_or_404(HotlineRequest, id=int(request_id))
        survey_taken = get_object_or_404(SurveyTaken, survey=survey,
                                                      request=event)
    except ValueError:
        raise Http404

    context.update({'survey_taken': survey_taken})

    return render(request, "mini_survey_data.html", context)
