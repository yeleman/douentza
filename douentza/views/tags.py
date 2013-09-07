#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from douentza.models import Tag, HotlineRequest


def all_tags(request):
    return HttpResponse(json.dumps([t.slug
                                    for t in Tag.objects.order_by('slug')]),
                        mimetype='application/json')


def tags_for(request, request_id):
    hotline_req = get_object_or_404(HotlineRequest, id=request_id)
    return HttpResponse(json.dumps([t.slug
                                    for t in hotline_req.tags.order_by('slug')]),
                        mimetype='application/json')


@csrf_exempt
@require_POST
def update_tags(request, request_id):
    hotline_req = get_object_or_404(HotlineRequest, id=request_id)
    tags = json.loads(request.body.decode())
    print(tags)
    hotline_req.tags.clear()
    for txttag in tags:
        try:
            tag = Tag.objects.get(slug=txttag)
        except Tag.DoesNotExist:
            tag = Tag.objects.create(slug=txttag)
        hotline_req.tags.add(tag)

    # clean up unused tags
    for tag in Tag.objects.all():
        if not tag.requests.count():
            tag.delete()
    return tags_for(request, request_id)
