#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import random

from django.conf import settings

from douentza.models import HotlineRequest
from douentza.utils import (event_type_from_message,
                            is_valid_number,
                            number_is_blacklisted,
                            operator_from_mali_number)
from douentza.views.fondasms import datetime_from_timestamp
from douentza.utils import normalize_phone_number


class UnableToCreateHotlineRequest(Exception):
    pass

# place holder for incoming phone numbers (phone device)
# with operator
INCOMING_NUMBERS_BY_OPERATOR = {}
INCOMING_NUMBERS_WITH_OPERATOR = {}


def automatic_reply_handler(payload):
    # called by automatic reply logic
    # if settings.FONDA_SEND_AUTOMATIC_REPLY_VIA_HANDLER
    # Can be used to fetch or forge reply when we need more than
    # the static FONDA_AUTOMATIC_REPLY_TEXT
    return None


def handle_incoming_sms(payload):
    # on SMS received
    return handle_sms_call(payload)


def handle_incoming_call(payload):
    # on call received
    return handle_sms_call(payload, event_type=HotlineRequest.TYPE_RING)


def handle_sms_call(payload, event_type=None):
    identity = normalize_phone_number(payload.get('from').strip())
    if not is_valid_number(identity) or number_is_blacklisted(identity):
        return

    message = payload.get('message').strip()
    if not len(message):
        message = None

    if event_type is None:
        event_type = event_type_from_message(message)

    phone_number = payload.get('phone_number')
    timestamp = payload.get('timestamp')
    received_on = datetime_from_timestamp(timestamp)
    operator = operator_from_mali_number(identity)

    try:
        existing = HotlineRequest.objects \
                                 .exclude(status=HotlineRequest.STATUS_HANDLED) \
                                 .get(identity=identity)
    except HotlineRequest.DoesNotExist:
        existing = None

    # if same number calls again before previous request has been treated
    # we add an additional request only
    if existing:
        existing.add_additional_request(request_type=event_type,
                                        sms_message=message)
        return

    try:
        HotlineRequest.objects.create(
            identity=identity,
            event_type=event_type,
            hotline_number=phone_number,
            received_on=received_on,
            sms_message=message,
            operator=operator)
    except Exception as e:
        raise UnableToCreateHotlineRequest(e)


def handle_outgoing_status_change(payload):
    # we don't store outgoing messages for now
    return


def handle_device_status_change(payload):
    # we don't track device changes for now
    return


def check_meta_data(payload):
    # we don't track device changes for now
    return


def reply_with_phone_number(payload):
    end_user_phone = payload.get('from')
    if end_user_phone is not None:
        return get_phone_number_for(operator_from_mali_number(end_user_phone))
    return None


def get_phone_number_for(operator):
    return random.choice(INCOMING_NUMBERS_BY_OPERATOR.get(operator, [None])) or None

for number in settings.FONDA_INCOMING_NUMBERS:
    operator = operator_from_mali_number(number)
    if not operator in INCOMING_NUMBERS_BY_OPERATOR.keys():
        INCOMING_NUMBERS_BY_OPERATOR.update({operator: []})
    INCOMING_NUMBERS_BY_OPERATOR[operator].append(number)
    INCOMING_NUMBERS_WITH_OPERATOR.update({number: operator})
