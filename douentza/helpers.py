#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from douentza.models import HotlineRequest


class UnableToCreateHotlineRequest(Exception):
    pass


def create_request(identity, event_type, received_on,
                   operator=None, message=None, phone_number=None):
    try:
        existing = HotlineRequest.objects \
                                 .exclude(status__in=HotlineRequest.DONE_STATUSES) \
                                 .get(identity=identity)
        cluster = existing.cluster
    except HotlineRequest.DoesNotExist:
        existing = None
        cluster = None

    # if same number calls again before previous request has been treated
    # we add an additional request only
    if existing:
        existing.add_additional_request(request_type=event_type,
                                        sms_message=message,
                                        created_on=received_on)
        # no text answer - retruning straight
        return existing

    try:
        return HotlineRequest.objects.create(
            identity=identity,
            event_type=event_type,
            hotline_number=phone_number,
            received_on=received_on,
            sms_message=message,
            operator=operator,
            cluster=cluster)
    except Exception as e:
        raise UnableToCreateHotlineRequest(e)
