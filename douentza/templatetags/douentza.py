#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime

from django import template, forms
from django.template.defaultfilters import stringfilter, date
from django.core.urlresolvers import reverse

from douentza.utils import clean_phone_number_str, COUNTRY_PREFIX

register = template.Library()


@register.filter(name='phone')
@stringfilter
def phone_number_formatter(number):
    ''' format phone number properly for display '''
    return clean_phone_number_str(number, skip_indicator=COUNTRY_PREFIX)


@register.filter(name='datepickerjs')
def auto_datetimepicker(field):
    if not isinstance(field.field, (forms.DateField, forms.DateTimeField)):
        return ''

    dirty = str(field.form.is_bound).lower()

    if isinstance(field.field.widget, forms.widgets.DateInput):
        return 'setupDatetimePicker({date_selector: "'+field.name+'", dirty: '+dirty+'});'
    elif isinstance(field.field.widget, forms.widgets.TimeInput):
        return 'setupDatetimePicker({time_selector: "'+field.name+'", dirty: '+dirty+'});'
    elif isinstance(field.field.widget, forms.widgets.SplitDateTimeWidget):
        return 'setupDatetimePicker({split_widget: true, split_selector: "'+field.name+'", dirty: '+dirty+'});'

    return ''


@register.filter(name='available_for')
def survey_is_available(survey, request):
    return survey.available_for(request)


@register.filter(name='taken')
def survey_is_taken(survey, request):
    try:
        return survey.taken(request)
    except:
        return ''


@register.filter(name='statuscss')
def cssclass_from_status(status):
    from douentza.models import HotlineRequest
    status_table = {
        HotlineRequest.STATUS_NEW_REQUEST: 'default',
        HotlineRequest.STATUS_NOT_ANSWERING: 'warning',
        HotlineRequest.STATUS_HANDLED: 'success',
        HotlineRequest.STATUS_IS_BUSY: 'warning',
        HotlineRequest.STATUS_BLACK_LIST: 'inverse',
        HotlineRequest.STATUS_GAVE_UP: 'danger'
    }

    return "label-{}".format(status_table.get(status, 'default'))


@register.filter(name='humandelta')
def human_delta(delta):
    if delta.days > 365:
        nby = delta.days // 365
        text = "{} an".format(nby)
        if nby > 1:
            text += "s"
        nbd = delta.days - nby * 365
        if nbd:
            text += " {} jours".format(nbd)
        return text
    else:
        return delta.days


@register.filter(name='eventdate')
def event_date(adate):
    return date(adate, "D d b, H\hi")


@register.filter(name='handleddate')
def event_handled_date(adate):
    return date(adate, "l d F Y à H\hi")


@register.filter(name='eventdateshort')
def event_date_short(adate):
    return date(adate, "D H\hi")


@register.filter(name='orderby')
def queryset_order_by(queryset, order_by):
    return queryset.order_by(order_by)


@register.filter(name='cachedfile')
def cached_file_path(slug):
    from douentza.models import CachedData
    try:
        return reverse('cached_file',
                       args=(CachedData.objects.get(slug=slug).value,))
    except:
        return ''


@register.filter(name='cachedslug')
def cached_slug_redirect(slug):
    return reverse('cached_slug', args=(slug,))


@register.filter(name='duration')
def duration(seconds):
    if seconds is None:
        return None
    else:
        seconds = int(seconds)

    data= {
         'days': 0,
         'hours': 0,
         'minutes': 0,
         'seconds': 0}
    if seconds > 86400:
        data['days'] = seconds // 86400
        seconds -= data['days'] * 86400
    if seconds > 3600:
        data['hours'] = seconds // 3600
        seconds -= data['hours'] * 3600
    if seconds > 60:
        data['minutes'] = seconds // 60
        seconds -= data['minutes'] * 60
    data['seconds'] = seconds

    s = ""
    if data['days']:
        s += "{}j ".format(data['days'])
    if data['hours']:
        s += "{}h ".format(data['hours'])
    if data['minutes']:
        s += "{}mn ".format(data['minutes'])
    if data['seconds']:
        s += "{}".format(data['seconds'])

    if not data['hours'] and not data['minutes']:
        s += "s"

    return s
