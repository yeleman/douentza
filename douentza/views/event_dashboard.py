#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from douentza.models import HotlineRequest, BlacklistedNumber, AdditionalRequest, CallbackAttempt
from douentza.utils import (start_or_end_day_from_date,
                            get_default_context,
                            to_jstimestamp)


@login_required()
def dashboard(request):
    context = get_default_context(page="event_dashboard")
    context.update({'all_events': all_events()})
    context.update({'now': to_jstimestamp(datetime.datetime.today())})
    return render(request, "event_dashboard.html", context)


def all_events():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    data_event = {'today_events': HotlineRequest.incoming.filter(received_on__gte=start_or_end_day_from_date(today, True),
                                                              received_on__lt=start_or_end_day_from_date(today, False)).all(),
                  'yesterday_events': HotlineRequest.incoming.filter(received_on__gte=start_or_end_day_from_date(yesterday, True),
                                                                 received_on__lt=start_or_end_day_from_date(yesterday, False)).all(),
                  'ancient_events': HotlineRequest.incoming.filter(received_on__lt=start_or_end_day_from_date(yesterday, True)).all()}
    data_event.update({'has_events': bool(len(data_event['today_events'])
                                     + len(data_event['yesterday_events'])
                                     + len(data_event['ancient_events']))})
    return data_event


@login_required()
def ping_json(request):
    try:
        since = datetime.datetime.fromtimestamp(int(request.GET.get('since')) / 1000)
    except:
        raise Http404

    try:
        excludes = json.loads(request.GET.get('exclude'))
    except:
        excludes = []

    def prep_request(request):
        d = request.to_dict()
        d.update({'html_row': render_to_string('event_row_dashboard.html',
                                               {'event': request})})
        return d
    events = [prep_request(r)
              for r in HotlineRequest.incoming.filter(received_on__gte=since)
                                     .exclude(id__in=excludes)]
    data = {
        'now': to_jstimestamp(datetime.datetime.today()),
        'events': events
    }
    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required()
def ping_html(request):

    now = datetime.datetime.now()

    try:
        since = datetime.datetime.fromtimestamp(int(request.GET.get('since')) / 1000)
    except:
        raise Http404

    nb_events = HotlineRequest.incoming.filter(received_on__gte=since).count() \
        + AdditionalRequest.objects.filter(created_on__gte=since).count() \
        + CallbackAttempt.objects.filter(created_on__gte=since).count()

    if nb_events:
        html = render_to_string('dashboard_table.html',
                                {'all_events': all_events()})
    else:
        html = None

    data = {
        'now': to_jstimestamp(now),
        'events': nb_events,
        'html': html}
    return HttpResponse(json.dumps(data), mimetype='application/json')


@login_required()
def change_event_status(request, request_id, new_status):
    if not new_status in HotlineRequest.STATUSES.keys():
        raise Http404
    try:
        event = HotlineRequest.objects \
                              .exclude(status=HotlineRequest.STATUS_HANDLED) \
                              .get(id=int(request_id))
        event.add_busy_call(new_status)
    except (HotlineRequest.DoesNotExist, ValueError):
        raise Http404

    if new_status == HotlineRequest.STATUS_BLACK_LIST:
        BlacklistedNumber.objects.create(identity=event.identity,
                                         call_count=1)
    return redirect('event_dashboard')
