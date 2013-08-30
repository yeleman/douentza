#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import datetime


def get_default_context(page=''):
    return {'page': page}


def datetime_range(start, stop=None, days=1):
    ''' return a list of dates incremented by 'days'

        start/stop = date or datetime
        days = increment number of days '''

    # stop at 00h00 today so we don't have an extra
    # point for today if the last period ends today.
    stop = stop or datetime.datetime(*datetime.date.today().timetuple()[:-4])

    while(start < stop):
        yield start
        start += datetime.timedelta(days)

    yield stop


def start_or_end_day_from_date(adate, start=True):
    return datetime.datetime(int(adate.year),
                             int(adate.month),
                             int(adate.day),
                             0 if start else 23,
                             0 if start else 59,
                             0 if start else 59)
