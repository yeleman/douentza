#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand

if PY2:
    import unicodecsv as csv
else:
    import csv

from douentza.models import Entity

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-a',
                    help='CSV file to import Administrative Entities from',
                    action='store',
                    dest='input_admin_file'),
        make_option('-c',
                    help='Delete all Entity fixtures first',
                    action='store_true',
                    dest='clear')
        )

    def handle(self, *args, **options):

        admin_headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                         'IDENT_ModifiedOn', 'IDENT_RegionName', 'IDENT_CercleName',
                         'IDENT_CommuneName',
                         'IDENT_HealthAreaCode', 'IDENT_HealthAreaName',
                         'IDENT_HealthAreaCenterDistance',
                         'IDENT_Latitude', 'IDENT_Longitude', 'IDENT_Geometry']

        input_admin_file = open(options.get('input_admin_file'), 'r')
        admin_csv_reader = csv.DictReader(input_admin_file, fieldnames=admin_headers)

        if options.get('clear'):
            print("Removing all entities...")
            Entity.objects.all().delete()

        type_matrix = {
            'region': 'region',
            'cercle': 'cercle',
            'commune': 'commune',
            'vfq': 'village',
        }

        def add_entity(entity_dict, is_admin):
            slug = entry.get('IDENT_Code')
            name = entry.get('IDENT_Name')
            type_slug = entry.get('IDENT_Type')
            parent_slug = entry.get('IDENT_ParentCode')
            latitude = entry.get('IDENT_Latitude')
            longitude = entry.get('IDENT_Longitude')

            entity = Entity.objects.create(slug=slug,
                                        name=name,
                                        entity_type=type_matrix.get(type_slug),
                                        latitude=latitude or None,
                                        longitude=longitude or None)
            if parent_slug and not parent_slug == 'mali':
                parent = Entity.objects.get(slug=parent_slug)
                entity.parent = parent

            entity.save()

            print(entity.name)

        print("Importing Admin Entities...")
        for entry in admin_csv_reader:
            if admin_csv_reader.line_num == 1:
                continue

            add_entity(entry, True)

