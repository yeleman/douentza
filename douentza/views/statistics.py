#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime
import csv

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Sum
from django.contrib.auth.decorators import login_required

from douentza.models import (HotlineRequest, Project, Survey, Entity, Ethnicity,
                            CachedData)
from douentza.utils import (get_default_context, datetime_range,
                            start_or_end_day_from_date, to_jstimestamp,
                            ethinicity_requests, communes_located_requests,
                            stats_per_age, percent_calculation, isoformat_date)


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

    hotlinerequest = HotlineRequest.objects

    try:
        last_event = hotlinerequest.latest('received_on')
    except HotlineRequest.DoesNotExist:
        last_event = []

    nb_total_events = hotlinerequest.count()
    nb_survey = Survey.objects.count()
    projects = Project.objects.all()
    nb_projects = projects.count()

    nb_unique_number = hotlinerequest.values('identity').distinct().count()

    sex_unknown = hotlinerequest.filter(sex=HotlineRequest.SEX_UNKNOWN).count()
    sex_male = hotlinerequest.filter(sex=HotlineRequest.SEX_MALE).count()
    sex_female = hotlinerequest.filter(sex=HotlineRequest.SEX_FEMALE).count()

    unknown_location_count = hotlinerequest.filter(location=None).count()
    unknown_location_percent = percent_calculation(unknown_location_count, nb_total_events)
    unknown_age = hotlinerequest.filter(age=None).count()
    unknown_age_percent = percent_calculation(unknown_age, nb_total_events)

    handled_hotline_request = hotlinerequest.filter(status=HotlineRequest.STATUS_HANDLED)
    sum_duration = handled_hotline_request.aggregate(Sum("duration"))
    average_duration = handled_hotline_request.aggregate(Avg("duration"))
    longest_duration = handled_hotline_request.aggregate(Max("duration"))
    short_duration = handled_hotline_request.aggregate(Min("duration"))

    hotlinerequest_project_count = [(project.name,
                                     hotlinerequest.filter(project=project).count(),
                                     percent_calculation(hotlinerequest.filter(project=project).count(), nb_projects))
                                     for project in projects]

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
                    'hotlinerequest_project_count': hotlinerequest_project_count,
                    'sum_duration': sum_duration,
                    'nb_ethinicity_requests': [ethinicity_requests(ethinicity)
                                               for ethinicity in Ethnicity.objects.all()],
                    'communes_located_requests': [communes_located_requests(commune)
                                                  for commune in list(Entity.objects.filter(entity_type='commune'))] +
                                                  [("Inconnue", unknown_location_count, unknown_location_percent)],
                    'general_stats_slug': "general_stats",
                    })

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


def export_general_stats_as_csv(filename):
    ''' export the csv file '''

    created_on = "created_on"
    sms_message = "sms_message"
    received_on = "received_on"
    identity = "identity"
    operator = "operator"
    age = "age"
    sex = "sex"
    duration = "duration"
    ethnicity_name = "ethnicity_name"
    ethnicity_slug = "ethnicity_slug"
    event_type = "event_type"
    responded_on = "responded_on"
    project = "project"
    status = "status"
    nb_cols_additional_request = 5
    nb_cols_tags = 15
    nb_cols_attempt = 5
    tag_total_nb = "tag_total_nb"
    attempt_nb_total = "attempt_nb_total"
    additional_nb_total = "additional_nb_total"

    names_until = lambda slug, nb, suffix=None: ["{slug}_{incr}".format(slug=slug, incr=incr)
                                    for incr in range(1, nb + 1)]
    prefix_list = lambda prefix, alist: ["{prefix}_{slug}".format(slug=slug, prefix=prefix)
                                         for slug in alist]

    tags_headers = names_until("tag", nb_cols_tags) + ["tags", tag_total_nb]
    entity_headers = prefix_list('location', ["slug", "type", "gps", "name",
                                              "latitude", "longitude", "parent"])

    additional_headers = [prefix + '_' + suffix
                         for prefix in names_until("additional_request", nb_cols_additional_request)
                         for suffix in [created_on, "request_type", sms_message]] + [additional_nb_total]

    attempt_headers = [prefix + '_' + suffix
                       for prefix in names_until("attempt", nb_cols_attempt)
                       for suffix in [created_on, status]] + [attempt_nb_total]

    headers = [received_on,
                identity,
                operator,
                age,
                sex,
                duration,
                ethnicity_name,
                ethnicity_slug,
                event_type,
                sms_message,
                responded_on,
                project,
                status]

    headers += tags_headers + entity_headers + additional_headers + attempt_headers

    csv_file = open(filename, 'w')
    csv_writer = csv.DictWriter(csv_file, headers)
    csv_writer.writeheader()

    for hotlinerequest in HotlineRequest.objects.order_by("-received_on"):
        data = {received_on: isoformat_date(hotlinerequest.received_on),
                identity: hotlinerequest.identity,
                operator: hotlinerequest.operator,
                age: hotlinerequest.age,
                sex: hotlinerequest.sex,
                duration: hotlinerequest.duration,
                event_type: hotlinerequest.event_type,
                sms_message: hotlinerequest.sms_message,
                responded_on: isoformat_date(hotlinerequest.responded_on),
                project: hotlinerequest.project,
                status: hotlinerequest.status,
                tag_total_nb: hotlinerequest.tags.count(),
                additional_nb_total: hotlinerequest.additionalrequests.count(),
                attempt_nb_total: hotlinerequest.callbackattempts.count(),
        }

        if hotlinerequest.ethnicity:
            data.update({'ethnicity_name': hotlinerequest.ethnicity.name,
                         'ethnicity_slug': hotlinerequest.ethnicity.slug})

        location = hotlinerequest.location
        if location:
            data.update({'location_slug': location.slug,
                         'location_type': location.entity_type,
                         'location_longitude': location.longitude,
                         'location_latitude': location.latitude,
                         'location_parent': location.parent,
                         'location_gps': location.get_geopoint(),
                         'location_name': location.name
                         })

        tags = hotlinerequest.tags.all()[:nb_cols_tags]
        for n, tag in enumerate(tags):
            data.update({'tag_{}'.format(n + 1): tag.slug})

        data.update({'tags': ", ".join([t.slug for t in tags])})

        attempts = hotlinerequest.callbackattempts.all()[:nb_cols_attempt]
        for n, attempt in enumerate(attempts):
            data.update({'attempt_{nb}_{status}'.format(nb=(n + 1), status=status): attempt.type_str(),
                         'attempt_{nb}_{created_on}'.format(nb=(n + 1),
                                                            created_on=created_on): isoformat_date(attempt.created_on)})

        additionalrequests = hotlinerequest.additionalrequests.all()[:nb_cols_additional_request]
        for n, additionalrequest in enumerate(additionalrequests):
            data.update({'additional_request_{nb}_request_type'.format(nb=(n + 1)): additionalrequest.event_type,
                        'additional_request_{nb}_{created_on}'.format(nb=(n + 1),
                                                                      created_on=created_on): isoformat_date(additionalrequest.created_on),
                        'additional_request_{nb}_{sms_message}'.format(nb=(n + 1),
                                                                       sms_message=sms_message ): additionalrequest.sms_message})

        csv_writer.writerow(data)
    csv_file.close()

    return filename
