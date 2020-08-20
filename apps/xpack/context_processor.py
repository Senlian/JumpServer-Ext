#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from  django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

def xpack_processor(request):
    context = {
        'XPACK_PLUGINS': []
    }
    return context
