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


def event(request):
    context = {'page': 'event'}
    events = HotlineEvent.objects.all()
    context.update({'events': events})
    return render(request, "event.html", context)


def events(request):
    date_start_end = lambda d, s=True, yest=False: \
        datetime.datetime(int(d.year), int(d.month), int(d.day -1) if yest else int(d.day),
                          0 if s else 23, 0 if s else 59, 0 if s else 59)
    d = datetime.date.today()

    data_event = {'today_event': [event.to_dict()
                                  for event in HotlineEvent.objects.filter(received_on__gte=date_start_end(d),
                                                                           received_on__lt=date_start_end(d, False)).all()],
                 'yesterday_event': [event.to_dict()
                                  for event in HotlineEvent.objects.filter(received_on__gte=date_start_end(d, True, True),
                                                                           received_on__lt=date_start_end(d, False, True)).all()],
                 'ancient_event': [event.to_dict()
                                  for event in HotlineEvent.objects.filter(received_on__lt=date_start_end(d, True, True)).all()]
                 }
    return HttpResponse(json.dumps(data_event), mimetype='application/json')

