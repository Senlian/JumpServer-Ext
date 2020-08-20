#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.db.models import F
from django.utils.translation import ugettext as _
from django import forms
from orgs.mixins.forms import OrgModelForm
from ..models import CiPermission

__all__ = [
    'JenkinsPermissionCreateUpdateForm',
]


class JenkinsPermissionCreateUpdateForm(OrgModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        users_field = self.fields.get('users')
        if self.instance:
            users_field.queryset = self.instance.users.all()
        else:
            users_field.queryset = []

    class Meta:
        model = CiPermission
        exclude = (
            'id', 'date_created', 'created_by', 'org_id'
        )
        widgets = {
            'users': forms.SelectMultiple(
                attrs={'class': 'users-select2', 'data-placeholder': _('User')}
            ),
            'user_groups': forms.SelectMultiple(
                attrs={'class': 'select2', 'data-placeholder': _('User group')}
            ),
            'cis': forms.SelectMultiple(
                attrs={'class': 'select2', 'data-placeholder': _('Jenkins job')}
            )
        }


