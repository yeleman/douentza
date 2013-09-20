#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime
import csv

import numpy
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404
from django.http import Http404

from douentza.models import (Survey, HotlineRequest, Question,
                             SurveyTaken, SurveyTakenData, CachedData)
from douentza.forms import MiniSurveyForm
from douentza.utils import get_default_context


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


def stats_for_surveys(request):
    context = get_default_context(page='stats_for_surveys')

    context.update({'surveys': Survey.validated.order_by('id')})

    return render(request, "stats_for_surveys.html", context)


def stats_for_survey(request, survey_id):
    context = get_default_context(page='stats_for_survey')

    try:
        survey = get_object_or_404(Survey, id=int(survey_id))
    except ValueError:
        raise Http404

    all_questions_data = CachedData.get_or_fallback(slug=survey.cache_slug,
                                                    fallback=[])
    context.update({'all_questions_data': all_questions_data,
                    'survey': survey})

    return render(request, "stats_for_survey.html", context)


def compute_survey_questions_data(survey):

    main_types = {
        Question.TYPE_STRING: 'string',
        Question.TYPE_TEXT: 'string',
        Question.TYPE_BOOLEAN: 'boolean',
        Question.TYPE_DATE : 'date',
        Question.TYPE_INTEGER: 'number',
        Question.TYPE_FLOAT: 'number',
        Question.TYPE_CHOICES: 'choice',
    }

    all_questions_data = []

    for question in survey.questions.order_by('-order', 'id'):
        questions_data = question.to_dict()
        questions_data.update({
            'nb_values': SurveyTakenData.objects.filter(question=question).count(),
            'nb_null_values': SurveyTakenData.objects.filter(question=question,
                                                             value__isnull=True).count(),
            'type_template': "ms_question_details_{}.html".format(main_types.get(question.question_type))})
        questions_data.update(custom_stats_for_type(question))
        all_questions_data.append(questions_data)

    return all_questions_data


def custom_stats_for_type(question):
    return {
        Question.TYPE_STRING: lambda x: {},
        Question.TYPE_TEXT: lambda x: {},
        Question.TYPE_BOOLEAN: _stats_for_boolean,
        Question.TYPE_DATE : _stats_for_date,
        Question.TYPE_INTEGER: _stats_for_number,
        Question.TYPE_FLOAT: _stats_for_number,
        Question.TYPE_CHOICES: _stats_for_choice,
    }.get(question.question_type)(question)


def _stats_for_boolean(question):
    data = {
        'nb_true': SurveyTakenData.objects.filter(question=question, value__exact=True).count(),
        'nb_false': SurveyTakenData.objects.filter(question=question, value__exact=False).count()
    }
    return data


def _stats_for_date(question):
    all_values = [v.value for v in SurveyTakenData.objects.filter(question=question)]
    first = numpy.min(all_values)
    last = numpy.max(all_values)
    span = last - first
    return {
        'first': first,
        'center': first + datetime.timedelta(days=span.days / 2),
        'span': span,
        'last': last
    }


def _stats_for_number(question):
    all_values = [v.value for v in SurveyTakenData.objects.filter(question=question)]
    return {
        'min': numpy.min(all_values),
        'max': numpy.max(all_values),
        'avg': numpy.mean(all_values),
        'median': numpy.median(all_values)
    }


def _stats_for_choice(question):
    data = {'choices_count': {}}
    for choice in question.questionchoices.order_by('id'):
        data['choices_count'].update({choice.slug: choice.to_dict()})
        data['choices_count'][choice.slug].update({
            'count': SurveyTakenData.objects.filter(question=question,
                                                    value__exact=choice.slug).count()})
    return data


def export_survey_as_csv(survey, filename):

    norm_header = lambda label: slugify(label)
    headers = [norm_header(q['label']) for q in survey.to_dict()['questions']]

    csv_file = open(filename, 'w')
    csv_writer = csv.DictWriter(csv_file, headers)
    csv_writer.writeheader()

    for survey_taken in survey.survey_takens.order_by('taken_on'):
        data = {}
        for question in survey_taken.survey.questions.order_by('-order', 'id'):
            data.update({
                norm_header(question.label): question.survey_taken_data.get(survey_taken=survey_taken).value})
        csv_writer.writerow(data)

    csv_file.close()

    return filename