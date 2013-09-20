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
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger

from douentza.models import (HotlineRequest, Ethnicity, Project, HotlineUser,
                             Entity, Survey, BlacklistedNumber,
                             SurveyTaken)
from douentza.utils import get_default_context, EMPTY_ENTITY, FlynsarmyPaginator
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
            project = form.cleaned_data.get('project')
            if not project is None:
                try:
                    project = Project.objects.get(id=int(project))
                except Project.DoesNotExist:
                    pass
            event.project = project
            event.sex = form.cleaned_data.get('sex')
            ethnicity = form.cleaned_data.get('ethnicity')
            if ethnicity is not None:
                try:
                    ethnicity = Ethnicity.objects.get(slug=ethnicity)
                except Ethnicity.DoesNotExist:
                    pass
            event.ethnicity = ethnicity
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

    try:
        handled_requests = HotlineRequest.handled_requests.all()
    except:
        raise Http404


    if request.method == "POST":
        try:
            identity = int(request.POST.get('identity').replace(' ', ''))
        except ValueError:
            identity = 1

        handled_requests = HotlineRequest.handled_requests.filter(identity__contains=identity)

    paginator = FlynsarmyPaginator(handled_requests, 25, adjacent_pages=10)

    page = request.GET.get('page')
    try:
        requests_paginator = paginator.page(page)
    except PageNotAnInteger:
        requests_paginator = paginator.page(1)
    except (EmptyPage, InvalidPage):
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
