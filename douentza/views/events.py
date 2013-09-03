#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render

from douentza.models import HotlineRequest
from douentza.utils import get_default_context


def display_event(request, event_id):

    try:
        event = HotlineRequest.objects.get(id=int(event_id))
    except:
        raise

    context = get_default_context(page="display_event")
    context.update({'event': event})
    return render(request, "event.html", context)