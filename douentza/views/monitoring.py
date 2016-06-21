#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime

from django.shortcuts import render

from douentza.models import SurveyTaken, HotlineRequest, HotlineUser
from douentza.utils import make_aware, today

NB_DAYS = 60


def summary(request):
    start = make_aware(today() - datetime.timedelta(days=NB_DAYS))

    users = HotlineUser.objects \
        .exclude(username__in=('admin', 'staff')) \
        .exclude(cluster__isnull=True)
    data = []

    for _ in range(NB_DAYS + 1):
        end = start + datetime.timedelta(days=1)
        qs = SurveyTaken.objects.filter(taken_on__gte=start, taken_on__lt=end)
        qs2 = HotlineRequest.objects.all()
        data.append({
            'day': start,
            'takens': qs.count(),
            'nb_received': qs2.filter(
                received_on__gte=start, received_on__lte=end).count(),
            'nb_responded': qs2.filter(
                responded_on__gte=start, responded_on__lte=end).count(),
            'counts': [(qs.filter(request__hotline_user=user).count())
                       for user in users]
            })

        start = end
    context = {'page': 'monitoring', 'data': reversed(data), 'users': users}
    return render(request, 'monitoring.html', context)
