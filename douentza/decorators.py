#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def staff_required(target):
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return target(request, *args, **kwargs)
        raise PermissionDenied
    return login_required(wrapper)
