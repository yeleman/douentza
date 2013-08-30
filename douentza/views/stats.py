#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse

from batbelt import to_timestamp

from douentza.models import HotlineEvent, HotlineResponse, Project, Survey
from douentza.utils import get_default_context, datetime_range


def get_graph_context():
    date_start_end = lambda d, s=True: \
        datetime.datetime(int(d.year), int(d.month), int(d.day),
                          0 if s else 23, 0 if s else 59, 0 if s else 59)

    try:
        start = HotlineEvent.objects.order_by('received_on')[0].received_on
    except IndexError:
        start = datetime.datetime.today()

    requests = []
    responses = []

    for date in datetime_range(start):
        ts = int(to_timestamp(date)) * 1000
        qcount = HotlineEvent.objects.filter(received_on__gte=date_start_end(date),
                                             received_on__lt=date_start_end(date, False)).count()
        scount = HotlineResponse.objects.filter(response_date__gte=date_start_end(date),
                                                response_date__lt=date_start_end(date, False)).count()
        requests.append((ts, qcount))
        responses.append((ts, scount))
    data_event = {'requests': requests,
                  'responses': responses}

    return data_event

def get_status_context():
    ''' return the context for status '''
    context = {}
    try:
        last_event = HotlineEvent.objects.latest('received_on')
    except HotlineEvent.DoesNotExist:
        last_event = []

    total_events = HotlineEvent.objects.count()
    total_prjects = Project.objects.count()
    total_survey = Survey.objects.count()
    total_unique_number = HotlineEvent.objects.values('identity').distinct().count()

    sex_unknown = HotlineResponse.objects.filter(sex=HotlineResponse.SEX_UNKNOWN).count()
    sex_male = HotlineResponse.objects.filter(sex=HotlineResponse.SEX_MALE).count()
    sex_female = HotlineResponse.objects.filter(sex=HotlineResponse.SEX_FEMALE).count()

    context.update({'last_event': last_event,
                    'total_events': total_events,
                    'total_prjects': total_prjects,
                    'total_survey': total_survey,
                    'total_unique_number': total_unique_number,
                    'sex_unknown': sex_unknown,
                    'sex_male': sex_male,
                    'sex_female': sex_female})
    return context


def stats(request):
    context = get_default_context(page='stats')

    context.update(get_status_context())

    return render(request, "stats.html", context)


def graph_data_json(request):
    ''' Return graph data in json '''

    return HttpResponse(json.dumps(get_graph_context()), mimetype='application/json')