#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import BasePermission

class CiPermission(BasePermission):
    cis = models.ManyToManyField(to="cis.JenkinsCi", related_name="granted_by_permissions", blank=False, verbose_name=_("Jenkins ci"))
    # users = models.ManyToManyField('users.User', related_name="granted_by_permissions", blank=True, verbose_name=_("User"))
    nodes = models.ManyToManyField(to="cis.JenkinsNode", related_name="granted_by_permissions", blank=False, verbose_name=_("Jenkins node"))
    class Meta:
        unique_together = [('org_id', 'name')]
        verbose_name = _('Jenkins permission')
        ordering = ('name',)

    def get_all_cis(self):
        return self.cis.all()

    def __str__(self):
        return self.name
