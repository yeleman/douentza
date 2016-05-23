#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re

from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from douentza.models import HotlineRequest, Survey
from douentza.utils import get_default_context


@login_required
def archives(request):

    context = get_default_context(page='archives')

    done_requests = HotlineRequest.done.order_by('-received_on')

    if request.method == "POST":
        search_string = re.sub(r'[^0-9]+', '', request.POST.get('identity'))
        done_requests = HotlineRequest.done.filter(
            identity__icontains=search_string)

    paginator = Paginator(done_requests, 25)

    page = request.GET.get('page')
    try:
        requests_paginator = paginator.page(page)
    except PageNotAnInteger:
        requests_paginator = paginator.page(1)
    except EmptyPage:
        requests_paginator = paginator.page(paginator.num_pages)

    context.update({"requests_paginator": requests_paginator})

    return render(request, "archives.html", context)


@login_required
def archived_request(request, request_id):

    try:
        event = get_object_or_404(HotlineRequest, id=int(request_id))
    except:
        raise Http404

    context = get_default_context(page="archived_request")
    context.update({"surveys": Survey.validated.order_by('id'),
                    "event": event})

    return render(request, "archived_request.html", context)
