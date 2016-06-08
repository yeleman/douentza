#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify

if PY2:
    import unicodecsv as csv
else:
    import csv

from douentza.models import Entity


def harmonize(name):
    return name.title()


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-f',
                    help='CSV file to import coordinates from',
                    action='store',
                    dest='input_file'),
        )

    def handle(self, *args, **options):

        headers = ['lga', 'coordinates', 'latitude', 'longitude']

        input_file = open(options.get('input_file'), 'r')
        csv_reader = csv.DictReader(input_file,
                                    fieldnames=headers)

        def get_parent(name, etype, parent=None):

            try:
                return Entity.objects.get(slug=slug)
            except:
                return Entity.objects.create(slug=slug,
                                             name=harmonize(name),
                                             entity_type=etype,
                                             parent=parent)

        print("Importing Entities Coordinates...")
        for entry in csv_reader:
            if csv_reader.line_num == 1:
                continue

            slug = slugify(entry.get('lga'))
            lga = Entity.objects.get(slug=slug, entity_type=Entity.TYPE_LGA)
            lga.latitude = float(entry.get('latitude'))
            lga.longitude = float(entry.get('longitude'))
            lga.save()

            print(lga.name)
