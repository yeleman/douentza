#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from douentza.models import Survey, QuestionChoice, Question, Project, BlacklistedNumber, HotlineRequest
from douentza.forms import (MiniSurveyInitForm, MiniSurveyAddQuestion,
                            AddProjectForm)
from douentza.utils import get_default_context


@login_required
def admin_surveys(request):
    context = get_default_context(page='admin_surveys')

    context.update({'surveys': Survey.objects.order_by('id')})

    if request.method == "POST":
        form = MiniSurveyInitForm(request.POST)
        if form.is_valid():
            survey = form.save()
            return redirect('admin_survey', survey.id)
        else:
            pass
    else:
        form = MiniSurveyInitForm()

    context.update({'form': form})

    return render(request, "admin_surveys.html", context)


@login_required
def admin_survey(request, survey_id):
    context = get_default_context(page='admin_survey')

    survey = get_object_or_404(Survey, id=int(survey_id),
                               status=Survey.STATUS_CREATED)

    context.update({'survey': survey})

    if request.method == "POST":
        form = MiniSurveyAddQuestion(request.POST)
        if form.is_valid():

            question = form.save(commit=False)
            question.survey = survey
            question.save()

            if question.question_type == question.TYPE_CHOICES:
                for slug, label in form.cleaned_data.get('question_choices').items():
                    try:
                        QuestionChoice.objects.create(slug=slug,
                                                      label=label,
                                                      question=question)
                    except:
                        pass  # means we already have that question in place
            return redirect('admin_survey', survey_id=survey.id)
        else:
            pass
    else:
        form = MiniSurveyAddQuestion()

    context.update({'form': form})

    return render(request, "admin_survey.html", context)


@login_required
def admin_delete_question(request, survey_id, question_id):

    survey = get_object_or_404(Survey, id=int(survey_id),
                               status=Survey.STATUS_CREATED)
    question = get_object_or_404(Question, id=int(question_id))

    if not question.survey == survey:
        raise Http404

    QuestionChoice.objects.filter(question=question).delete()
    question.delete()

    return redirect('admin_survey', survey_id=survey.id)


@login_required
def admin_survey_validate(request, survey_id):

    survey = get_object_or_404(Survey, id=int(survey_id),
                               status=Survey.STATUS_CREATED)

    if not survey.questions.count():
        return redirect('admin_survey', survey.id)

    survey.status = Survey.STATUS_READY
    survey.save()

    return redirect('admin_surveys')


@login_required
def admin_survey_toggle(request, survey_id):

    survey = get_object_or_404(Survey, id=int(survey_id),
                               status__in=(Survey.STATUS_READY,
                                           Survey.STATUS_DISABLED))

    survey.status = Survey.STATUS_READY \
        if survey.status == Survey.STATUS_DISABLED else Survey.STATUS_DISABLED
    survey.save()

    return redirect('admin_surveys')


@login_required
def admin_projects(request):

    context = get_default_context(page='add_project')

    context.update({'projects': Project.objects.order_by('id')})

    if request.method == "POST":
        form = AddProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_projects')
        else:
            pass
    else:
        form = AddProjectForm()

    context.update({'form': form})

    return render(request, "admin_projects.html", context)


@login_required()
def admin_blacklist(request, blacknum_id=None):
    context = get_default_context(page='blacklist')
    if blacknum_id:
        try:
            blacknum = BlacklistedNumber.objects.get(id=blacknum_id)
            identity = blacknum.identity
            blacknum.delete()
        except:
            raise Http404

        for hotline_request in HotlineRequest.objects.filter(identity=identity,
                                                             status=HotlineRequest.STATUS_BLACK_LIST):
            hotline_request.status = hotline_request.previous_status()
            hotline_request.save()
        return redirect("blacklist")

        messages.success(request,
                         "{identity} à été retiré la liste noire".format(
                         identity=blacknum.identity))
    context.update({'blacknums': BlacklistedNumber.objects.all()})

    return render(request, "blacklist.html", context)
