#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import json

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from douentza.models import (HotlineRequest, Ethnicity, Project, HotlineUser,
                             Entity, Survey)
from douentza.utils import get_default_context, EMPTY_ENTITY
from douentza.forms import BasicInformationForm


def display_event(request, event_id):

    try:
        event = get_object_or_404(HotlineRequest, id=int(event_id))
    except:
        raise Http404

    context = get_default_context(page="display_event")
    context.update({'event': event})
    context.update({'surveys': Survey.objects.all()})

    if request.method == "POST":
        form = BasicInformationForm(request.POST)
        if form.is_valid():
            event = form.cleaned_data.get('request_id')

            event.status = HotlineRequest.STATUS_HANDLED
            # event.hotline_user = HotlineUser.objects.get(username=request.user)
            event.responded_on = form.cleaned_data.get('responded_on')
            event.age = form.cleaned_data.get('age')
            try:
                event.project = Project.objects.get(id=int(form.cleaned_data.get('project')))
            except ValueError:
                pass
            event.sex = form.cleaned_data.get('sex')
            event.ethnicity = Ethnicity.objects.get(slug=form.cleaned_data.get('ethnicity'))
            event.duration = form.cleaned_data.get('duration')
            event.location = form.cleaned_data.get('village')
            event.save()
            return redirect('event_dashboard')
    else:
        form = BasicInformationForm(initial={'request_id': event_id})

    context.update({"form": form})

    return render(request, "event.html", context)


def entities_api(request, parent_slug=None):
    ''' JSON list of Entity whose parent has the slug provided '''

    response = [{'slug': EMPTY_ENTITY, 'name': "INCONNU"}] + \
        [{'slug': e.slug, 'name': e.name}
            for e in Entity.objects.filter(parent__slug=parent_slug)]

    return HttpResponse(json.dumps(response), mimetype='application/json')
