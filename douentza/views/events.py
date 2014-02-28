#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from douentza.models import HotlineRequest, HotlineUser, Entity, Survey
from douentza.utils import get_default_context, EMPTY_ENTITY
from douentza.forms import BasicInformationForm


@login_required()
def display_request(request, request_id):

    try:
        event = get_object_or_404(HotlineRequest, id=int(request_id))
    except:
        raise Http404

    context = get_default_context(page="display_request")
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
            event.cluster = request.user.slug
            event.save()
            return redirect('dashboard')
    else:
        form = BasicInformationForm(initial={'request_id': request_id})

    context.update({"form": form})

    return render(request, "request.html", context)


@login_required()
def entities_api(request, parent_slug=None):
    ''' JSON list of Entity whose parent has the slug provided '''

    response = [{'slug': EMPTY_ENTITY, 'name': "INCONNU"}] + \
        [{'slug': e.slug, 'name': e.name}
            for e in Entity.objects.filter(parent__slug=parent_slug)]

    return HttpResponse(json.dumps(response), mimetype='application/json')
