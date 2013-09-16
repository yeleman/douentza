#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.decorators import login_required

from douentza.models import (HotlineRequest, Project, Survey, Entity, Ethnicity)
from douentza.utils import (get_default_context, datetime_range,
                            start_or_end_day_from_date, to_jstimestamp,
                            ethinicity_requests, communes_located_requests,
                            stats_per_age, percent_calculation)


def get_event_responses_counts():

    try:
        start = HotlineRequest.objects.order_by('received_on')[0].received_on
    except IndexError:
        start = datetime.datetime.today()

    events = []
    responses = []

    for date in datetime_range(start):
        ts = to_jstimestamp(date)
        qcount = HotlineRequest.objects.filter(received_on__gte=start_or_end_day_from_date(date),
                                               received_on__lt=start_or_end_day_from_date(date, False)).count()
        scount = HotlineRequest.objects.filter(responded_on__gte=start_or_end_day_from_date(date),
                                               responded_on__lt=start_or_end_day_from_date(date, False)).count()
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

    unknown_location_count = HotlineRequest.objects.filter(location=None).count()
    total = HotlineRequest.objects.all().count()

    unknown_location_percent = percent_calculation(unknown_location_count, total)
    unknown_age = HotlineRequest.objects.filter(age=None).count()
    unknown_age_percent = percent_calculation(unknown_age, total)

    handled_hotline_request = HotlineRequest.objects.filter(status=HotlineRequest.STATUS_HANDLED)
    sum_duration = handled_hotline_request.aggregate(Sum("duration"))
    average_duration = handled_hotline_request.aggregate(Avg("duration"))
    longest_duration = handled_hotline_request.aggregate(Max("duration"))
    short_duration = handled_hotline_request.aggregate(Min("duration"))

    under_18 = stats_per_age(0, 18)
    stats_19_25 = stats_per_age(19, 25)
    stats_26_40 = stats_per_age(26, 40)
    stats_41_55 = stats_per_age(41, 55)
    other_56 = stats_per_age(56, 180)

    context.update({'last_event': last_event,
                    'nb_total_events': nb_total_events,
                    'nb_projects': nb_projects,
                    'nb_survey': nb_survey,
                    'nb_unique_number': nb_unique_number,
                    'sex_unknown': sex_unknown,
                    'sex_male': sex_male,
                    'sex_female': sex_female,
                    'under_18': under_18,
                    'stats_19_25': stats_19_25,
                    'stats_26_40': stats_26_40,
                    'stats_41_55': stats_41_55,
                    'other_56': other_56,
                    'unknown_age': unknown_age,
                    'average_duration': average_duration,
                    'longest_duration': longest_duration,
                    'short_duration': short_duration,
                    'unknown_age_percent': unknown_age_percent,
                    'sum_duration': sum_duration,
                    'nb_ethinicity_requests': [ethinicity_requests(ethinicity)
                                               for ethinicity in Ethnicity.objects.all()],
                    'communes_located_requests': [communes_located_requests(commune)
                                                  for commune in list(Entity.objects.filter(entity_type='commune'))] +
                                                  [("Inconnue", unknown_location_count, unknown_location_percent)],})
    return context


@login_required()
def dashboard(request):
    context = get_default_context(page='statistics')

    context.update(get_statistics_dict())

    return render(request, "statistics.html", context)


@login_required()
def event_response_counts_json(request):

    return HttpResponse(json.dumps(get_event_responses_counts()),
                        mimetype='application/json')
