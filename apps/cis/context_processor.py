# -*- coding: utf-8 -*-
#
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser


def jenkins_processor(request):
    # Setting default pk
    context = {
        'SINGLE_TYPES': ['PT_RADIO', 'PT_SINGLE_SELECT'],
        'MULTI_TYPES': ['PT_MULTI_SELECT', 'PT_CHECKBOX'],
        'TEXT_TYPES': ['ET_TEXT_BOX'],
    }
    return context
