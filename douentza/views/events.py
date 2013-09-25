#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re
import json

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from douentza.models import (HotlineRequest, HotlineUser,
                             Entity, Survey, BlacklistedNumber)
from douentza.utils import get_default_context, EMPTY_ENTITY
from douentza.forms import BasicInformationForm


@login_required()
def display_event(request, request_id):

    try:
        event = get_object_or_404(HotlineRequest, id=int(request_id))
    except:
        raise Http404

    context = get_default_context(page="display_event")
    context.update({'event': event})
    context.update({'surveys': Survey.validated.order_by('id')})
    if request.method == "POST":
        form = BasicInformationForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data.get('request_id')
            event.status = HotlineRequest.STATUS_HANDLED
            event.hotline_user = get_object_or_404(HotlineUser,
                                                   username=request.user)
            event.responded_on = form.cleaned_data.get('responded_on')
            event.age = form.cleaned_data.get('age')
            event.project = form.cleaned_data.get('project')
            event.sex = form.cleaned_data.get('sex')
            event.ethnicity = form.cleaned_data.get('ethnicity')
            event.duration = form.cleaned_data.get('duration')
            event.location = form.cleaned_data.get('village')
            event.save()
            return redirect('event_dashboard')
    else:
        form = BasicInformationForm(initial={'request_id': request_id})

    context.update({"form": form})

    return render(request, "event.html", context)


@login_required()
def entities_api(request, parent_slug=None):
    ''' JSON list of Entity whose parent has the slug provided '''

    response = [{'slug': EMPTY_ENTITY, 'name': "INCONNU"}] + \
        [{'slug': e.slug, 'name': e.name}
            for e in Entity.objects.filter(parent__slug=parent_slug)]

    return HttpResponse(json.dumps(response), mimetype='application/json')


@login_required()
def blacklist(request, blacknum_id=None):
    context = get_default_context(page='blacklist')
    if blacknum_id:
        try:
            blacknum = BlacklistedNumber.objects.get(id=blacknum_id)
            blacknum.delete()
        except:
            raise Http404

        try:
            hquest = HotlineRequest.objects.get(identity=blacknum.identity)
        except:
            raise Http404
        hquest.status = HotlineRequest.STATUS_NEW_REQUEST
        hquest.save()
        return redirect("blacklist")

        messages.success(request,
                         "{identity} à été retirer la liste noire".format(identity=blacknum.identity))
    context.update({'blacknums': BlacklistedNumber.objects.all()})

    return render(request, "blacklist.html", context)


@login_required()
def archives(request):

    context = get_default_context(page='archives')

    done_requests = HotlineRequest.done.order_by('-received_on')

    if request.method == "POST":
        search_string = re.sub(r'[^0-9]+', '', request.POST.get('identity'))
        done_requests = HotlineRequest.done.filter(identity__icontains=search_string)

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


@login_required()
def display_handled_request(request, request_id):

    try:
        event = get_object_or_404(HotlineRequest, id=int(request_id))
    except:
        raise Http404

    context = get_default_context(page="display_handled_request")
    context.update({"surveys": Survey.validated.order_by('id'),
                    "event": event})

    return render(request, "display_handled_request.html", context)
