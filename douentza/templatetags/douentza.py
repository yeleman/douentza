#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import template, forms
from django.template.defaultfilters import stringfilter

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
def survey_is_available(survey, request):
    try:
        return survey.taken(request)
    except:
        return ''
