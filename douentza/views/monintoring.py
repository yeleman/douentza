#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from datetime import timedelta, datetime
from django.shortcuts import render

from douentza.models import SurveyTaken, HotlineRequest, HotlineUser


def monintoring(request):
    start = datetime(2015, 12, 15)
    users = HotlineUser.objects.all()
    data = []
    for day in range(33):
        end = start + timedelta(days=1)
        qs = SurveyTaken.objects.filter(taken_on__gte=start, taken_on__lt=end)
        data.append({
            'day': start,
            "takens": qs.count(),
            "nb_received": HotlineRequest.objects.filter(received_on__gte=start, received_on__lte=end).count(),
            "nb_responded": HotlineRequest.objects.filter(responded_on__gte=start, responded_on__lte=end).count(),
            "counts": [(qs.filter(request__hotline_user=user).count()) for user in users]
            })
        start = end
    context = {'page': "monintoring", "data": data, "users": users}
    return render(request, "monintoring.html", context)
