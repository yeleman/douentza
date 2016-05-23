#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from douentza.models import HotlineRequest, AdditionalRequest, Project

NO_OFFICE_HOURS = range(8) + range(17, 24)
logger = logging.getLogger(__name__)

nb_req_gen_at_hour = lambda hour, cls: \
    cls.objects.filter(created_on__hour=hour).count()

nb_req_at_hour = lambda hour: nb_req_gen_at_hour(hour, HotlineRequest)
nb_add_at_hour = lambda hour: nb_req_gen_at_hour(hour, AdditionalRequest)

# nb_req_noofficehours = lambda: \
#     sum([nb_req_at_hour(hour) for hour in NO_OFFICE_HOURS])

# nb_add_noofficehours = lambda: \
#     sum([nb_add_at_hour(hour) for hour in NO_OFFICE_HOURS])

# nb_attempts_noofficehours = nb_req_noofficehours() + nb_add_noofficehours()


def is_office_hours(adate):
        if adate.weekday in (0, 6):
            return False
        return adate.hour not in NO_OFFICE_HOURS


def nb_req_noofficehours():
    return len([hr
                for hr in HotlineRequest.objects.all()
                if not is_office_hours(hr.created_on)])


def nb_add_noofficehours():
    return len(
        [hr
         for hr in AdditionalRequest.objects.all()
         if not is_office_hours(hr.created_on)])


def nb_bad_req_noofficehours():
    return len([hr
                for hr in HotlineRequest.objects.filter(
                    responded_on__isnull=True)
                if not is_office_hours(hr.created_on)])


def nb_bad_add_noofficehours():
    return len(
        [hr
         for hr in AdditionalRequest.objects.filter(
             event__created_on__isnull=True)
         if not is_office_hours(hr.created_on)])


def nb_only_outside_office_hours_notanswered():
    return len([hr
                for hr in HotlineRequest.objects.all()
                if not is_office_hours(hr.created_on)
                and len([ar for ar in hr.additionalrequests.all()
                         if is_office_hours(ar.created_on)]) == 0])


nb_not_answered = lambda: HotlineRequest.objects.filter(
    responded_on__isnull=True).count()

print("nb hotline requests outside office hours", nb_req_noofficehours())
print("nb additional requests outside office hours", nb_add_noofficehours())
print("never answered requests (unable to reach back)", nb_not_answered())
print("never answered with only outside office hours attemps",
      nb_only_outside_office_hours_notanswered())


def times_between_creation_first_additional():
    return [
        (t[1] - t[0]).total_seconds()
        for t in [(hr.created_on,
                  getattr(hr.additionalrequests.order_by('created_on').first(),
                          'created_on', None))
                  for hr in HotlineRequest.objects.all()]
        if t[1] is not None]


def projects_call_csv():
    print("\n".join(["{},{}".format(
        p.name, HotlineRequest.objects.filter(project=p).filter(
            responded_on__isnull=False).count())
        for p in Project.objects.all()]))


def nb_of_request_nounits():
    canyou = "Peux-tu "
    return sum([
        HotlineRequest.objects.filter(
            event_type__in=(HotlineRequest.TYPE_CALL_ME,
                            HotlineRequest.TYPE_CHARGE_ME)).count(),
        AdditionalRequest.objects.filter(
            request_type__in=(HotlineRequest.TYPE_CALL_ME,
                              HotlineRequest.TYPE_CHARGE_ME)).count(),
        HotlineRequest.objects.filter(
            event_type=HotlineRequest.TYPE_SMS,
            sms_message__startswith=canyou).count(),
        AdditionalRequest.objects.filter(
            request_type=HotlineRequest.TYPE_SMS,
            sms_message__startswith=canyou).count(),
        ])
