#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re
import datetime

from django.utils import timezone
from py3compat import string_types


NB_CHARS_VALID_NUMBER = 8  # bellow, number is considered invalid
COUNTRY_PREFIX = '234'  # home phone prefix
EMPTY_ENTITY = '00000000'  # must not exist in fixtures
ORANGE = 'orange'
MALITEL = 'malitel'
UNKNOWN = 'unknown'
OPERATORS = {UNKNOWN: "Unknown"}
ALL_COUNTRY_CODES = [1242, 1246, 1264, 1268, 1284, 1340, 1345, 1441, 1473,
                     1599, 1649, 1664, 1670, 1671, 1684, 1758, 1767, 1784,
                     1809, 1868, 1869, 1876, 1, 20, 212, 213, 216, 218, 220,
                     221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231,
                     232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242,
                     243, 244, 245, 248, 249, 250, 251, 252, 253, 254, 255,
                     256, 257, 258, 260, 261, 262, 263, 264, 265, 266, 267,
                     268, 269, 27, 290, 291, 297, 298, 299, 30, 31, 32, 33,
                     34, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359,
                     36, 370, 371, 372, 373, 374, 375, 376, 377, 378, 380,
                     381, 382, 385, 386, 387, 389, 39, 40, 41, 420, 421, 423,
                     43, 44, 45, 46, 47, 48, 49, 500, 501, 502, 503, 504,
                     505, 506, 507, 508, 509, 51, 52, 53, 54, 55, 56, 57, 58,
                     590, 591, 592, 593, 595, 597, 598, 599, 60, 61, 62, 63,
                     64, 65, 66, 670, 672, 673, 674, 675, 676, 677, 678, 679,
                     680, 681, 682, 683, 685, 686, 687, 688, 689, 690, 691,
                     692, 7, 81, 82, 84, 850, 852, 853, 855, 856, 86, 870,
                     880, 886, 90, 91, 92, 93, 94, 95, 960, 961, 962, 963,
                     964, 965, 966, 967, 968, 970, 971, 972, 973, 974, 975,
                     976, 977, 98, 992, 993, 994, 995, 996, 998]
# some countries are prefixed with 0 locally
ZERO_PREFIXED_CONTRIES = [234]


def event_type_from_message(message):
    from douentza.models import HotlineRequest
    if message is None:
        return HotlineRequest.TYPE_RING

    message = message.strip()
    call_me_tpl_orange = "Peux-tu me rappeler au numero suivant"
    charge_me_tpl_orange = "Peux-tu recharger mon compte"
    call_me_tpl_malitel = "Rappellez moi s'il vous plait au numero suivant"
    am_tpl_orange = "Messagerie Vocale:"

    if message.startswith(call_me_tpl_orange) \
       or message.startswith(call_me_tpl_malitel):
        return HotlineRequest.TYPE_CALL_ME
    if message.startswith(charge_me_tpl_orange):
        return HotlineRequest.TYPE_CHARGE_ME
    if message.startswith(am_tpl_orange):
        return HotlineRequest.TYPE_RING
    if not message:
        return HotlineRequest.TYPE_RING
    return HotlineRequest.TYPE_SMS


def get_default_context(page='', **kwargs):
    from douentza.models import HotlineRequest
    context = {'page': page,
               'events_count': HotlineRequest.incoming.count()}
    for key, value in kwargs.items():
        context.update({key: value})
    return context


def datetime_range(start, stop=None, days=1):
    ''' return a list of dates incremented by 'days'

        start/stop = date or datetime
        days = increment number of days '''

    # remove offset
    start = start.replace(tzinfo=None)
    start = make_aware(start)
    if stop:
        stop = stop.replace(tzinfo=None)

    # stop at 00h00 today so we don't have an extra
    # point for today if the last period ends today.
    stop = stop or datetime.datetime(*datetime.date.today().timetuple()[:-4])
    stop = make_aware(stop)

    while(start < stop):
        yield start
        start += datetime.timedelta(days)

    yield stop


def start_or_end_day_from_date(adate, start=True):
    return make_aware(datetime.datetime(int(adate.year),
                                        int(adate.month),
                                        int(adate.day),
                                        0 if start else 23,
                                        0 if start else 59,
                                        0 if start else 59))


def clean_phone_number_str(number, skip_indicator=None):
    ''' properly formated for visualization: (xxx) xx xx xx xx '''

    def format(number):
        # Nigerian format
        if len(number) == 11:
            return "{a} {b} {c}".format(
                a=number[0:4], b=number[4:7], c=number[7:])
        if len(number) % 2 == 0:
            span = 2
        else:
            span = 3
        # use NBSP
        return " ".join(["".join(number[i:i + span])
                        for i in range(0, len(number), span)])

    indicator, clean_number = clean_phone_number(number)
    if indicator and indicator != skip_indicator:
        return "(%(ind)s) %(num)s" \
               % {'ind': indicator,
                  'num': format(clean_number)}

    return format(clean_number)


def is_valid_number(number):
    ''' checks if number is valid for HOTLINE_NUMBERS

        We want to get rid of operator spam '''
    if number is None:
        return False
    indicator, clean_number = clean_phone_number(number)
    return len(clean_number) >= NB_CHARS_VALID_NUMBER


def number_is_blacklisted(number):
    from douentza.models import BlacklistedNumber
    identity = normalize_phone_number(number)
    if BlacklistedNumber.objects.filter(identity=identity).count():
        b = BlacklistedNumber.objects.get(identity=identity)
        b.call_count += 1
        b.save()
        return True
    else:
        return False


def phone_number_is_int(number):
    ''' whether number is in international format '''
    if re.match(r'^[+|(]', number):
        return True
    if re.match(r'^\d{1,4}\.\d+$', number):
        return True
    return False


def get_phone_number_indicator(number):
    ''' extract indicator from number or "" '''
    for indic in ALL_COUNTRY_CODES:
        if number.startswith("%s" % indic) or number.startswith("+%s" % indic):
            return str(indic)
    return ""


def clean_phone_number(number):
    ''' return (indicator, number) cleaned of space and other '''

    # clean up
    if not isinstance(number, string_types):
        number = number.__str__()

    # cleanup markup
    clean_number = re.sub(r'[^\d\+]', '', number)

    indicator = None
    if phone_number_is_int(clean_number):
        h, indicator, clean_number = \
            clean_number.partition(get_phone_number_indicator(clean_number))

    # add-back missing zero prefix
    if (indicator in ZERO_PREFIXED_CONTRIES
        or int(COUNTRY_PREFIX) in ZERO_PREFIXED_CONTRIES) \
            and not clean_number.startswith('0'):
        clean_number = "0{}".format(clean_number)

    return (indicator, clean_number)


def normalize_phone_number(number_text):
    def join_phone_number(prefix, number, force_intl=True):
        if not prefix and force_intl:
            prefix = COUNTRY_PREFIX
        return '+%s%s' % (prefix, number)

    indicator, clean_number = clean_phone_number(number_text)
    if indicator is None:
        indicator = int(COUNTRY_PREFIX)

    if (indicator in ZERO_PREFIXED_CONTRIES) and clean_number.startswith('0'):
        clean_number = clean_number[1:]

    return join_phone_number(indicator, clean_number)


def operator_from_mali_number(number, default=ORANGE):
    ''' ORANGE or MALITEL based on the number prefix '''

    indicator, clean_number = clean_phone_number(number)
    if indicator is not None and indicator != str(COUNTRY_PREFIX):
        return default

    malitel_prefixes = [2, 6, 98, 99]
    orange_prefixes = [7, 9, 4, 8, 90, 91]

    for prefix in malitel_prefixes:
        if clean_number.startswith(str(prefix)):
            return MALITEL

    for prefix in orange_prefixes:
        if clean_number.startswith(str(prefix)):
            return ORANGE

    return default


def operator_from_nigeria_number(number, default=UNKNOWN):
    return default


def to_jstimestamp(adate):
    if adate is not None:
        return int(to_timestamp(adate)) * 1000


def to_timestamp(dt):
    """
    Return a timestamp for the given datetime object.
    """
    if dt is not None:
        dt = make_aware(dt)
        ref = make_aware(datetime.datetime(1970, 1, 1))
        return (dt - ref).total_seconds()


def hotline_requests_qs():
    from douentza.models import HotlineRequest
    return HotlineRequest.objects.all()
    # .filter(survey_takens__isnull=False)


def ethinicity_requests(ethnicity):
    qs = hotline_requests_qs()
    count = qs.filter(ethnicity=ethnicity).count()
    total = qs.count()
    percent = percent_calculation(count, total)
    return ethnicity, count, percent


def lga_located_requests(entity):
    qs = hotline_requests_qs()
    count = qs.filter(location__in=entity.get_descendants(True)).count()
    total = qs.count()
    percent = percent_calculation(count, total)
    return entity, count, percent


def stats_per_age(begin=0, end=0):
    qs = hotline_requests_qs()
    count = qs.filter(age__gte=begin, age__lte=end).count()
    total = qs.count()

    percent = percent_calculation(count, total)
    return count, percent


def percent_calculation(value, total):
    try:
        percent = (value * 100) / total
    except ZeroDivisionError:
        percent = 0
    return percent


def isoformat_date(date):
    try:
        return date.isoformat()
    except:
        return None


def make_aware(dt):
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def today():
    return datetime.datetime(
        *[int(x) for x in datetime.date.today().timetuple()[:4]])
