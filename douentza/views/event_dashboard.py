#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json
import datetime

from django.http import HttpResponse
from django.shortcuts import render

from douentza.models import HotlineEvent
from douentza.utils import start_or_end_day_from_date, get_default_context


def dashboard(request):
    context = get_default_context(page="event_dashboard")
    return render(request, "event_dashboard.html", context)


def events_json(request):

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    data_event = {'today_event': [event.to_dict() for event in
        HotlineEvent.objects.filter(received_on__gte=start_or_end_day_from_date(today, True),
                                    received_on__lt=start_or_end_day_from_date(today, False)).all()],
                 'yesterday_event': [event.to_dict() for event in
        HotlineEvent.objects.filter(received_on__gte=start_or_end_day_from_date(yesterday, True),
                                    received_on__lt=start_or_end_day_from_date(yesterday, False)).all()],
                 'ancient_event': [event.to_dict() for event in
        HotlineEvent.objects.filter(received_on__lt=start_or_end_day_from_date(yesterday, True)).all()]}

    return HttpResponse(json.dumps(data_event), mimetype='application/json')
