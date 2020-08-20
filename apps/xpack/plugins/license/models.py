#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.conf import settings


class License():
    @classmethod
    def has_valid_license(self):
        return settings.LICENSE_VALID
