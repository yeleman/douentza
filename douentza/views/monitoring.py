#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from datetime import timedelta, datetime
from django.shortcuts import render

from douentza.models import SurveyTaken, HotlineRequest, HotlineUser


def summary(request):
    # static
    start = datetime(2015, 12, 15)
    usernames = ['abba', 'kani', 'abdramane', 'amadou']

    users = HotlineUser.objects.filter(username__in=usernames)
    data = []
    for day in range(32):
        end = start + timedelta(days=1)
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
    context = {'page': 'monitoring', 'data': data, 'users': users}
    return render(request, 'monitoring.html', context)
