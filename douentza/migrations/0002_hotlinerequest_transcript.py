# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-18 09:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douentza', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotlinerequest',
            name='transcript',
            field=models.TextField(blank=True, null=True),
        ),
    ]
