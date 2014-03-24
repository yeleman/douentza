#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import datetime
import json

from django.conf import settings
from django.utils.text import slugify
from django.core.management.base import BaseCommand

from douentza.views.surveys_stats import (export_survey_as_csv,
                                    compute_survey_questions_data)
from douentza.views.statistics import (export_general_stats_as_csv,
                                       get_event_responses_counts,
                                       get_geojson_statistics)
from douentza.models import Survey, CachedData


class Command(BaseCommand):
    help = "Generate cold-fusion stats for the site"

    def handle(self, *args, **options):

        def remove_previous_file(cdata):
            if cdata.data_type == CachedData.TYPE_FILE and cdata.value:
                filename = os.path.join(settings.CACHEDDATA_FOLDER, cdata.value)
                try:
                    os.remove(filename)
                    return True
                except:
                    return False

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

            fcache, _ = CachedData.objects.get_or_create(slug=survey.cache_file_slug)
            remove_previous_file(fcache) # clean-up first
            fcache.data_type = CachedData.TYPE_FILE
            fcache.value = fname
            fcache.created_on = now
            fcache.save()

            # Survey Stats Data
            ocache, _ = CachedData.objects.get_or_create(slug=survey.cache_slug)
            ocache.value = compute_survey_questions_data(survey)
            ocache.data_type = CachedData.TYPE_OBJECT
            ocache.created_on = now
            ocache.save()

        ###
        ## General stats
        ###

        fname = 'general_stats-{date}.csv'.format(date=datestr)

        filename = os.path.join(settings.CACHEDDATA_FOLDER, fname)
        export_general_stats_as_csv(filename=filename)

        gcache, _ = CachedData.objects.get_or_create(slug=slugify("general_stats"))
        remove_previous_file(gcache) # clean-up first
        gcache.data_type = CachedData.TYPE_FILE
        gcache.value = fname
        gcache.created_on = now
        gcache.save()


        # General Stats Graph
        fname = 'general-stats-graph-{date}.json'.format(date=datestr)
        filename = os.path.join(settings.CACHEDDATA_FOLDER, fname)
        json.dump(get_event_responses_counts(), open(filename, 'w'))

        jcache, _ = CachedData.objects.get_or_create(slug=slugify("general_stats_graph"))
        remove_previous_file(jcache) # clean-up first
        jcache.data_type = CachedData.TYPE_FILE
        jcache.value = fname
        jcache.created_on = now
        jcache.save()

        ###
        ## GeoJSON
        ###
        fname = 'public_geojson-statistics-{date}.json'.format(date=datestr)
        filename = os.path.join(settings.CACHEDDATA_FOLDER, fname)
        json.dump(get_geojson_statistics(), open(filename, 'w'))

        jcache, _ = CachedData.objects.get_or_create(slug=slugify("geojson_statistics"))
        remove_previous_file(jcache) # clean-up first
        jcache.data_type = CachedData.TYPE_FILE
        jcache.value = fname
        jcache.created_on = now
        jcache.save()

