#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.http import Http404
from django.shortcuts import redirect, get_object_or_404

from douentza.models import CachedData


def cached_data_lookup(request, slug):
    cdata = get_object_or_404(CachedData, slug=slug)

    if not cdata.data_type == CachedData.TYPE_FILE:
        raise Http404

    return redirect('cached_file', cdata.value)
