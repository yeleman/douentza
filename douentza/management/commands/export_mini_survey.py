#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

from django.utils.text import slugify
from django.core.management.base import BaseCommand
from optparse import make_option

from douentza.views.surveys import export_survey_as_csv
from douentza.models import Survey


class Command(BaseCommand):
    help = "Export a mini survey data in CSV"
    option_list = BaseCommand.option_list + (
        make_option('-f', '--filename',
                    action="store",
                    dest='filename',
                    default=None,
                    help='Output file to write export to. Use .csv'),
        make_option('-s', '--survey',
                    action="store",
                    dest='survey_id',
                    help='ID of Survey in DB.')
        )

    def handle(self, *args, **options):

        datestr = datetime.datetime.now().strftime('%Y-%m-%d-%Hh%M')
        filename = options.get('filename')
        survey_id = options.get('survey_id')

        try:
            survey = Survey.objects.get(id=int(survey_id))
        except (ValueError, Survey.DoesNotExist) as e:
            print(e)
            return

        if filename is None:
            slug = slugify(survey.title)
            filename = "minisurvey_{slug}_{date}.csv".format(date=datestr,
                                                             slug=slug)

        print(export_survey_as_csv(survey=survey, filename=filename))
