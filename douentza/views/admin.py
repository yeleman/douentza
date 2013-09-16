#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from douentza.models import Survey
from douentza.forms import MiniSurveyInitForm
from douentza.utils import get_default_context


@login_required
def admin_surveys(request):
    context = get_default_context(page='admin_surveys')

    context.update({'surveys': Survey.objects.all()})

    if request.method == "POST":
        form = MiniSurveyInitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_surveys')
        else:
            pass
    else:
        form = MiniSurveyInitForm()

    context.update({'form': form})

    return render(request, "admin_surveys.html", context)
