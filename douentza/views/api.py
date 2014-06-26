#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging
import json

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from douentza.models import HotlineRequest, Project, Ethnicity, Entity
from douentza.utils import operator_from_mali_number, normalize_phone_number

logger = logging.getLogger(__name__)

PROJECT = Project.objects.get(id=9)

@csrf_exempt
def events_api(request):

    def error(message):
        return HttpResponse(json.dumps({'status': 'error',
                                        'message': message}),
                            content_type='application/json')
    def resp(payload):
        return HttpResponse(json.dumps(payload),
                            content_type='application/json')

    payload = {
        'status': None,
        'message': None
    }

    try:
        jsdata = json.loads(request.body.decode())
    except:
        return error("Unable to decode sent data")

    if jsdata.get('action') in ('create', 'new'):
        # create event with phone number
        phone_number = normalize_phone_number(jsdata.get('phone_number'))
        email = jsdata.get('email', None)

        if phone_number is None or not len(phone_number.strip()):
            return error("phone_number is required for registration")

        # retrieve existing events
        qs = HotlineRequest.objects.filter(identity=phone_number,
                                           project=PROJECT)
        if qs.count() > 0:
            req = qs.last()
            req.add_additional_request(HotlineRequest.TYPE_WEB, None)
            payload.update({
                'status': 'duplicate',
                'message': "Already registered. Additionnal request recorded.",
                'event_id': req.id
            })
            return resp(payload)
        else:
            received_on = timezone.now()
            operator = operator_from_mali_number(phone_number)
            try:
                req = HotlineRequest.objects.create(
                    identity=phone_number,
                    event_type=HotlineRequest.TYPE_WEB,
                    hotline_number=None,
                    received_on=received_on,
                    sms_message=None,
                    operator=operator,
                    project=PROJECT,
                    email=email,
                    cluster=None)
            except Exception as e:
                return error("Internal error in creating event: {}".format(e))
            payload.update({
                'status': 'created',
                'message': "Event created",
                'event_id': req.id
            })
            return resp(payload)
    elif jsdata.get('action') in ('update',):
        # update event with ID
        try:
            req = HotlineRequest.objects.get(id=int(jsdata.get('event_id', None)))
        except:
            return error("Unable to retrieve request #{}"
                         .format(jsdata.get('event_id')))

        ethnicity = Ethnicity.get_or_none(jsdata.get('ethnicity', None))

        try:
            age = int(jsdata.get('age', None))
        except:
            age = None

        if not jsdata.get('gender', None) in HotlineRequest.SEXES.keys():
            gender = None

        location = Entity.get_or_none(jsdata.get('location', None))

        if ethnicity or age is not None or gender:
            req.ethnicity = ethnicity
            req.sex = jsdata.get('gender', HotlineRequest.SEX_UNKNOWN)
            req.age = age
            req.location = location
            req.save()
            payload.update({
                'status': 'updated',
                'message': "Updated details for Event #{}".format(req.id),
                'event_id': req.id
            })
            return resp(payload)
        else:
            return error("Nothing to update")
    elif jsdata.get('action') in ('ping',):
        payload.update({
            'status': 'success',
            'message': "Nothing to do"
        })
        return resp(payload)
    else:
        return error("No action matching `{}`".format(jsdata.get('action')))

    return HttpResponse(json.dumps(payload),
                        content_type='application/json')
