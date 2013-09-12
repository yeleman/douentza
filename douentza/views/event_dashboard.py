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

from douentza.models import HotlineRequest, BlacklistedNumber
from douentza.utils import start_or_end_day_from_date, get_default_context


@login_required()
def dashboard(request):
    context = get_default_context(page="event_dashboard")
    context.update({'all_events': all_events()})
    return render(request, "event_dashboard.html", context)


def all_events():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    data_event = {'today_events': HotlineRequest.incoming.filter(received_on__gte=start_or_end_day_from_date(today, True),
                                                              received_on__lt=start_or_end_day_from_date(today, False)).all(),
                  'yesterday_events': HotlineRequest.incoming.filter(received_on__gte=start_or_end_day_from_date(yesterday, True),
                                                                 received_on__lt=start_or_end_day_from_date(yesterday, False)).all(),
                  'ancient_events': HotlineRequest.incoming.filter(received_on__lt=start_or_end_day_from_date(yesterday, True)).all()}
    return data_event


@login_required()
def events_json(request):
    return HttpResponse(json.dumps(all_events()), mimetype='application/json')


@login_required()
def change_event_status(request, event_id, new_status):
    if not new_status in HotlineRequest.STATUSES.keys():
        raise Http404
    try:
        event = HotlineRequest.objects \
                              .exclude(status=HotlineRequest.STATUS_HANDLED) \
                              .get(id=int(event_id))
        event.add_busy_call(new_status)
    except (HotlineRequest.DoesNotExist, ValueError):
        raise Http404

    if new_status == HotlineRequest.STATUS_BLACK_LIST:
        BlacklistedNumber.objects.create(identity=event.identity,
                                         call_count=1)
    return redirect('event_dashboard')
