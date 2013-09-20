#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import datetime

from django.conf import settings
from django.utils.text import slugify
from django.core.management.base import BaseCommand

from douentza.views.surveys import (export_survey_as_csv,
                                    compute_survey_questions_data)
from douentza.models import Survey, CachedData


class Command(BaseCommand):
    help = "Generate cold-fusion stats for the site"

    def handle(self, *args, **options):

        now = datetime.datetime.now()
        datestr = now.strftime('%Y-%m-%d-%Hh%M')

        ###
        ## SURVEYS
        ###
        for survey in Survey.validated.all():

            # Survey Export File
            fname = 'ms{id}_{slug}-{date}.csv'.format(id=survey.id,
                                                      slug=slugify(survey.title),
                                                      date=datestr)
            filename = os.path.join(settings.CACHEDDATA_FOLDER, fname)
            export_survey_as_csv(survey=survey,
                                 filename=filename)

            cache, _ = CachedData.objects.get_or_create(slug=survey.cache_file_slug)
            cache.data_type = CachedData.TYPE_FILE
            cache.value = fname
            cache.cached_on = now
            cache.save()

            # Survey Stats Data
            cache, _ = CachedData.objects.get_or_create(slug=survey.cache_slug)
            cache.value = compute_survey_questions_data(survey)
            cache.data_type = CachedData.TYPE_OBJECT
            cache.cached_on = now
            cache.save()
