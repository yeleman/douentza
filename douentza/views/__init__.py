#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.template import RequestContext
from django.shortcuts import render_to_response

import douentza.views.admin
import douentza.views.api
import douentza.views.archives
import douentza.views.cached_data
import douentza.views.dashboard
import douentza.views.events
import douentza.views.monitoring
import douentza.views.statistics
import douentza.views.surveys
import douentza.views.surveys_stats
import douentza.views.tags
import douentza.views.reports


def handler404(request):
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response
