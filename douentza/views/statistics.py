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


def export_general_stats_as_csv(request):
    ''' export the csv file '''
    import csv
    from douentza.models import HotlineRequest
    filename = "export_data.csv"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename={filename}'.format(filename=filename)

    def numbering_name(prefix, suffix):

        if isinstance(suffix, list):
            values = suffix
        elif isinstance(suffix, int):
            values = range(1, suffix + 1)
        else:
            raise ValueError("la fonction numbering_name n'accepte \
                              qu'une liste ou un entier comme argument")
        return ["{prefix}_{suffix}".format(prefix=prefix, suffix=suffix)
                for suffix in values]

    tags_headers = numbering_name("tag", 15) + ["tags", "nb. tag"]
    entity_headers = numbering_name('location', ["slug", "id", "type", "nb", "gps",
                                                 "name", "latitude", "longitude", "parent"])
    additonal_headers = numbering_name("additional_request", 5) + ["additional_nb_total"]
    attempt_headers = numbering_name("attempt", 5) + ["attempt_nb_total"]

    headers = ["received_on",
                "identity",
                "operator",
                "age",
                "sex",
                "duration",
                "location",
                "ethnicity",
                "event_type",
                "sms_message",
                "responded_on",
                "project",
                "status"]
    headers += tags_headers + entity_headers + additonal_headers + attempt_headers

    writer = csv.writer(response)
    writer.writerow(headers)

    for hotlinerequest in HotlineRequest.objects.all():
        tags = [tag.slug for tag in hotlinerequest.tags.all()]
        data = [hotlinerequest.received_on,
                hotlinerequest.identity,
                hotlinerequest.operator,
                hotlinerequest.age,
                hotlinerequest.sex,
                hotlinerequest.duration,
                hotlinerequest.location,
                hotlinerequest.ethnicity,
                hotlinerequest.event_type,
                hotlinerequest.sms_message,
                hotlinerequest.responded_on,
                hotlinerequest.project,
                hotlinerequest.status]


        writer.writerow(data)
    response.close()

    return response


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