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
                    help='CSV file to import Administrative Entities from',
                    action='store',
                    dest='input_admin_file'),
        make_option('-c',
                    help='Delete all Entity fixtures first',
                    action='store_true',
                    dest='clear')
        )

    def handle(self, *args, **options):

        admin_headers = ['state', 'lga', 'ward']

        input_admin_file = open(options.get('input_admin_file'), 'r')
        admin_csv_reader = csv.DictReader(input_admin_file,
                                          fieldnames=admin_headers)

        if options.get('clear'):
            print("Removing all entities...")
            Entity.objects.all().delete()

        def get_parent(name, etype, parent=None):
            slug = slugify(name)
            try:
                return Entity.objects.get(slug=slug)
            except:
                return Entity.objects.create(slug=slug,
                                             name=harmonize(name),
                                             entity_type=etype,
                                             parent=parent)

        print("Importing Admin Entities...")
        for entry in admin_csv_reader:
            if admin_csv_reader.line_num == 1:
                continue

            state = get_parent(entry.get('state'), Entity.TYPE_STATE)
            lga = get_parent(entry.get('lga'), Entity.TYPE_LGA, parent=state)
            ward = get_parent(entry.get('ward'), Entity.TYPE_WARD, parent=lga)

            print(ward.name)
