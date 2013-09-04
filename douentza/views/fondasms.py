#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json
import datetime

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


def fondasms_tester(request):
    return render(request, 'fonda_tester.html', {})


@csrf_exempt
def fondasms_handler(request):

    from douentza.fondahandlers import (handle_incoming_call,
                                        handle_incoming_sms,
                                        handle_outgoing_status_change,
                                        handle_device_status_change)

    from pprint import pprint as pp ; pp(list(request.POST.items()))

    action = request.POST.get("action")
    handler = lambda x: None
    outgoings = []

    if action == "incoming":
        if request.POST.get('message_type') == 'call':
            handler = handle_incoming_call
        if request.POST.get('message_type') == 'sms':
            handler = handle_incoming_sms
        outgoings += handle_automatic_reply(request.POST) or []
    elif action == "outgoing":
        pass
    elif action == 'send_status':
        handler = handle_outgoing_status_change
    elif action == 'device_status':
        handler = handle_device_status_change
    else:
        return HttpResponse(json.dumps({}), mimetype='application/json')

    try:
        outgoings += handler(request.POST) or []
        if not isinstance(outgoings, list):
            outgoings = []
    except Exception as e:
        response = {'error': {'message': str(e)}}
        return HttpResponse(json.dumps(response),
                            mimetype='application/json',
                            status=500)

    response = {"events": [{"event": "send",
                            "messages": outgoings}]}

    from pprint import pprint as pp ; pp(response)

    return HttpResponse(json.dumps(response),
                        mimetype='application/json')


def outgoing_for(to, message, ident=None, priority=0):
    outgoing = {'to': to,
                'message': message}
    if ident is not None:
        outgoing.update({'id': ident})
    if priority:
        outgoing.update({'priority': priority})
    return outgoing


def handle_automatic_reply(payload):

    from douentza.fondahandlers import automatic_reply_handler

    if not settings.FONDA_SEND_AUTOMATIC_REPLY:
        return []

    message = None
    if settings.FONDA_SEND_AUTOMATIC_REPLY_VIA_HANDLER:
        message = automatic_reply_handler(payload)
    elif len(settings.FONDA_AUTOMATIC_REPLY_TEXT):
        message = settings.FONDA_AUTOMATIC_REPLY_TEXT

    if message:
        return [outgoing_for(to=payload.get('from'),
                             message=message)]

    return []


def datetime_from_timestamp(timestamp):
    try:
        return datetime.datetime.fromtimestamp(int(timestamp) / 1000)
    except (TypeError, ValueError):
        return None
    return None
