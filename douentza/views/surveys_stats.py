#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

import numpy
from django.utils.text import slugify
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from py3compat import PY2

if PY2:
    import unicodecsv as csv
else:
    import csv

from douentza.models import (Survey, Question,
                             SurveyTakenData, CachedData)
from douentza.utils import get_default_context, isoformat_date


@login_required
def stats_for_surveys(request):
    context = get_default_context(page='stats_for_surveys')

    context.update({'surveys': Survey.validated.order_by('id')})

    return render(request, "stats_for_surveys.html", context)


@login_required
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

    def _safe_percent(numerator, denominator):
        try:
            return numerator / denominator * 100
        except:
            return 0

    def custom_stats_for_type(question, total):
        return {
            Question.TYPE_STRING: lambda x, y: {},
            Question.TYPE_TEXT: lambda x, y: {},
            Question.TYPE_BOOLEAN: _stats_for_boolean,
            Question.TYPE_DATE : _stats_for_date,
            Question.TYPE_INTEGER: _stats_for_number,
            Question.TYPE_FLOAT: _stats_for_number,
            Question.TYPE_CHOICES: _stats_for_choice,
            Question.TYPE_MULTI_CHOICES: _stats_for_multi_choice,
        }.get(question.question_type)(question, total)


    def _stats_for_boolean(question, total):
        nb_true = SurveyTakenData.objects.filter(question=question,
                                                 value__exact=True).count()
        nb_false = SurveyTakenData.objects.filter(question=question,
                                                  value__exact=False).count()
        data = {
            'nb_true': nb_true,
            'percent_true': _safe_percent(nb_true, total),
            'nb_false': nb_false,
            'percent_false': _safe_percent(nb_false, total)
        }
        return data


    def _stats_for_date(question, total):
        all_values = [v.value
                      for v in SurveyTakenData.objects.filter(question=question)
                      if v.value is not None]
        if len(all_values):
            first = numpy.min(all_values)
            last = numpy.max(all_values)
            span = last - first
            center = first + datetime.timedelta(days=span.days / 2)
        else:
            first = last = span = center = None
        return {
            'first': first,
            'center': center,
            'span': span,
            'last': last
        }


    def _stats_for_number(question, total):
        all_values = [v.value
                      for v in SurveyTakenData.objects.filter(question=question)
                      if v.value is not None]
        if not len(all_values):
            return {'min': None,
                    'max': None,
                    'avg': None,
                    'median': None}
        return {
            'min': numpy.min(all_values),
            'max': numpy.max(all_values),
            'avg': numpy.mean(all_values),
            'median': numpy.median(all_values)
        }


    def _stats_for_choice(question, total):
        data = {'choices_count': {}}
        for choice in question.questionchoices.order_by('id'):
            count = SurveyTakenData.objects.filter(question=question,
                                                   value__exact=choice.slug).count()
            data['choices_count'].update({choice.slug: choice.to_dict()})
            data['choices_count'][choice.slug].update({
                'count': count,
                'percent': _safe_percent(count, total)})
        return data

    def _stats_for_multi_choice(question, total):
        data = {'choices_count': {}}
        for choice in question.questionchoices.order_by('id'):
            data['choices_count'].update({choice.slug: choice.to_dict()})
            data['choices_count'][choice.slug].update({
                'count': sum([1 for answer in SurveyTakenData.objects.filter(question=question)
                              if choice.slug in answer.value])})
        return data

    main_types = {
        Question.TYPE_STRING: 'string',
        Question.TYPE_TEXT: 'string',
        Question.TYPE_BOOLEAN: 'boolean',
        Question.TYPE_DATE : 'date',
        Question.TYPE_INTEGER: 'number',
        Question.TYPE_FLOAT: 'number',
        Question.TYPE_CHOICES: 'choice',
        Question.TYPE_MULTI_CHOICES: 'multi_choice',
    }

    all_questions_data = []

    for question in survey.questions.order_by('-order', 'id'):
        questions_data = question.to_dict()
        total = SurveyTakenData.objects.filter(question=question).count()
        nb_null = SurveyTakenData.objects.filter(question=question,
                                                 value__isnull=True).count()
        questions_data.update({
            'nb_values': total,
            'nb_null_values': nb_null,
            'percent_null_values': _safe_percent(nb_null, total),
            'type_template': "ms_question_details_{}.html".format(main_types.get(question.question_type))})
        questions_data.update(custom_stats_for_type(question, total))
        all_questions_data.append(questions_data)

    return all_questions_data


def export_survey_as_csv(survey, filename):

    norm_header = lambda label: slugify(label)
    meta_headers = ['meta_received_on', 'meta_responded_on', 'meta_operator',
                    'meta_cluster', 'meta_project', 'meta_age', 'meta_sex',
                    'meta_call_duration', 'meta_ethnicity', 'meta_region',
                    'meta_cercle', 'meta_commune', 'meta_village', 'meta_gps']
    headers = meta_headers + [norm_header(q['label']) for q in survey.to_dict()['questions']]

    def norm_value(value):
        if isinstance(value, list):
            return ",".join(value)
        return value

    csv_file = open(filename, 'w')
    if PY2:
        csv_writer = csv.DictWriter(csv_file, headers, encoding='utf-8')
    else:
        csv_writer = csv.DictWriter(csv_file, headers)
    csv_writer.writeheader()

    for survey_taken in survey.survey_takens.order_by('taken_on'):
        data = {
            'meta_received_on': isoformat_date(survey_taken.request.received_on),
            'meta_responded_on': isoformat_date(survey_taken.request.responded_on),
            'meta_operator': survey_taken.request.operator,
            'meta_cluster': survey_taken.request.cluster,
            'meta_project': survey_taken.request.project,
            'meta_age': survey_taken.request.age,
            'meta_sex': survey_taken.request.sex,
            'meta_call_duration': survey_taken.request.duration,
            'meta_ethnicity': survey_taken.request.ethnicity.slug,
            'meta_region': getattr(survey_taken.request.location, 'get_region', lambda: None)(),
            'meta_cercle': getattr(survey_taken.request.location, 'get_cercle', lambda: None)(),
            'meta_commune': getattr(survey_taken.request.location, 'get_commune', lambda: None)(),
            'meta_village': getattr(survey_taken.request.location, 'get_village', lambda: None)(),
            'meta_gps': getattr(survey_taken.request.location, 'get_geopoint', lambda: None)(),
        }
        for question in survey_taken.survey.questions.order_by('-order', 'id'):
            data.update({
                norm_header(question.label): norm_value(question.survey_taken_data.get(survey_taken=survey_taken).value)})
        csv_writer.writerow(data)

    csv_file.close()

    return filename
