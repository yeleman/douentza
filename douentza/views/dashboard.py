#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from douentza.models import (HotlineRequest, BlacklistedNumber,
                             AdditionalRequest, CallbackAttempt,
                             Cluster)
from douentza.utils import (start_or_end_day_from_date,
                            get_default_context,
                            to_jstimestamp)
from douentza.decorators import staff_required


def all_events(user):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    if user.cluster:
        hotlinerequests = HotlineRequest.incoming \
            .filter(cluster=user.cluster).exclude(cluster=None)
    else:
        hotlinerequests = HotlineRequest.incoming.all()
    data_event = {
        'today_events': hotlinerequests.filter(
            received_on__gte=start_or_end_day_from_date(today, True),
            received_on__lt=start_or_end_day_from_date(today, False)).all(),
        'yesterday_events': hotlinerequests.filter(
            received_on__gte=start_or_end_day_from_date(yesterday, True),
            received_on__lt=start_or_end_day_from_date(
                yesterday, False)).all(),
        'ancient_events': hotlinerequests.filter(
            received_on__lt=start_or_end_day_from_date(yesterday, True)).all(),
        'unsorted_events': HotlineRequest.incoming.filter(cluster=None).all()
    }
    data_event.update({'has_events': bool(
        len(data_event['today_events']) +
        len(data_event['yesterday_events']) +
        len(data_event['ancient_events']) +
        len(data_event['unsorted_events']))})
    return data_event


@login_required
def dashboard(request):
    user = request.user
    context = get_default_context(page="dashboard")
    clusters = Cluster.objects
    if hasattr(request.user.cluster, 'slug'):
        clusters = clusters.exclude(slug=request.user.cluster.slug)
    clusters = clusters.all()
    context.update({'all_events': all_events(user),
                    'clusters': clusters})
    context.update({'now': to_jstimestamp(datetime.datetime.today())})
    return render(request, "dashboard.html", context)


@staff_required
def ping_json(request):
    try:
        since = datetime.datetime.fromtimestamp(
            int(request.GET.get('since')) / 1000)
    except:
        raise Http404

    try:
        excludes = json.loads(request.GET.get('exclude'))
    except:
        excludes = []

    def prep_request(request):
        d = request.to_dict()
        d.update({'html_row': render_to_string('dashboard_table_row.html',
                                               {'event': request})})
        return d
    events = [prep_request(r)
              for r in HotlineRequest.incoming.filter(received_on__gte=since)
                                     .exclude(id__in=excludes)]
    data = {
        'now': to_jstimestamp(datetime.datetime.today()),
        'events': events
    }
    return JsonResponse(data)


@staff_required
def ping_html(request):

    now = datetime.datetime.now()

    try:
        since = datetime.datetime.fromtimestamp(
            int(request.GET.get('since')) / 1000)
    except:
        raise Http404

    nb_events = HotlineRequest.incoming.filter(received_on__gte=since).count() \
        + AdditionalRequest.objects.filter(created_on__gte=since).count() \
        + CallbackAttempt.objects.filter(created_on__gte=since).count()

    if nb_events:
        clusters = Cluster.objects
        if hasattr(request.user.cluster, 'slug'):
            clusters = clusters.exclude(slug=request.user.cluster.slug)
        clusters = clusters.all()
        html = render_to_string('dashboard_table.html',
                                {'all_events': all_events(request.user),
                                 'clusters': clusters})
    else:
        html = None

    data = {
        'now': to_jstimestamp(now),
        'events': nb_events,
        'html': html}
    return JsonResponse(data)


@staff_required
def change_event_status(request, request_id, new_status):
    if new_status not in HotlineRequest.STATUSES.keys():
        raise Http404
    try:
        event = HotlineRequest.objects \
                              .exclude(status=HotlineRequest.STATUS_HANDLED) \
                              .get(id=int(request_id))
        event.add_busy_call(new_status)
    except (HotlineRequest.DoesNotExist, ValueError):
        raise Http404

    if new_status == HotlineRequest.STATUS_BLACK_LIST:
        BlacklistedNumber.add_to_identy(event.identity)
    return redirect('dashboard')


@staff_required
def sorted_location(request, request_id, cluster_slug):
    try:
        event = HotlineRequest.objects \
                              .exclude(status=HotlineRequest.STATUS_HANDLED) \
                              .get(id=int(request_id))
        event.add_cluster(cluster_slug)
    except (HotlineRequest.DoesNotExist, ValueError):
        raise Http404

    return redirect('dashboard')
