#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render, get_object_or_404
from django.http import Http404

from douentza.models import Survey
from douentza.forms import MiniSurveyForm
from douentza.utils import get_default_context


def survey_form(request, survey_id):
    context = get_default_context(page="mini_survey")

    try:
        survey = get_object_or_404(Survey, id=int(survey_id))
    except ValueError:
        raise Http404

    from pprint import pprint as pp ; pp(survey.to_dict())

    if request.method == "POST":
        form = MiniSurveyForm(request.POST, survey=survey.to_dict())
        if form.is_valid():
            print("VALID !!!!!")
            from pprint import pprint as pp ; pp(form.cleaned_data)
        else:
            print("PAS VALIDE")
    else:
        form = MiniSurveyForm(survey=survey.to_dict())

    from pprint import pprint as pp ; pp(form.as_p())

    context.update({'form': form,
                    'survey': survey})

    return render(request, "mini_survey.html", context)
