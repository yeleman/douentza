#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.static import serve

from douentza.models import CachedData


def cached_data_lookup(request, slug):
    cdata = get_object_or_404(CachedData, slug=slug)

    if not cdata.data_type == CachedData.TYPE_FILE:
        raise Http404

    return redirect('cached_file', cdata.value)


def serve_cached_file(request, fname=None, public=False):
    if not fname.startswith('public_'):
        return login_required(do_serve_file_no_auth(request, fname))
    return do_serve_file_no_auth(request, fname)


def do_serve_file_no_auth(request, fname=None):
    if settings.SERVE_CACHED_FILES:
        return serve(request, fname, settings.CACHEDDATA_FOLDER, True)
    response = HttpResponse()
    del response['content-type']
    response['X-Accel-Redirect'] = "/protected/{fname}".format(fname=fname)
    return response