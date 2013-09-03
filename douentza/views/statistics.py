#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse

from douentza.models import HotlineRequest, Project, Survey
from douentza.utils import get_default_context, datetime_range, start_or_end_day_from_date, to_timestamp


def get_event_responses_counts():

    try:
        start = HotlineRequest.objects.order_by('received_on')[0].received_on
    except IndexError:
        start = datetime.datetime.today()

    events = []
    responses = []

    for date in datetime_range(start):
        ts = int(to_timestamp(date)) * 1000
        qcount = HotlineRequest.objects.filter(received_on__gte=start_or_end_day_from_date(date),
                                             received_on__lt=start_or_end_day_from_date(date, False)).count()
        scount = HotlineRequest.objects.filter(response_date__gte=start_or_end_day_from_date(date),
                                                response_date__lt=start_or_end_day_from_date(date, False)).count()
        events.append((ts, qcount))
        responses.append((ts, scount))
    event_response_data = {'events': events,
                           'responses': responses}

    return event_response_data

def get_statistics_dict():
    context = {}
    try:
        last_event = HotlineRequest.objects.latest('received_on')
    except HotlineRequest.DoesNotExist:
        last_event = []

    nb_total_events = HotlineRequest.objects.count()
    nb_projects = Project.objects.count()
    nb_survey = Survey.objects.count()
    nb_unique_number = HotlineRequest.objects.values('identity').distinct().count()

    sex_unknown = HotlineRequest.objects.filter(sex=HotlineRequest.SEX_UNKNOWN).count()
    sex_male = HotlineRequest.objects.filter(sex=HotlineRequest.SEX_MALE).count()
    sex_female = HotlineRequest.objects.filter(sex=HotlineRequest.SEX_FEMALE).count()

    context.update({'last_event': last_event,
                    'nb_total_events': nb_total_events,
                    'nb_projects': nb_projects,
                    'nb_survey': nb_survey,
                    'nb_unique_number': nb_unique_number,
                    'sex_unknown': sex_unknown,
                    'sex_male': sex_male,
                    'sex_female': sex_female})
    return context


def dashboard(request):
    context = get_default_context(page='statistics')

    context.update(get_statistics_dict())

    return render(request, "statistics.html", context)


def event_response_counts_json(request):

    return HttpResponse(json.dumps(get_event_responses_counts()),
                        mimetype='application/json')
