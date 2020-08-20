#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from ..models import Organization
from django.utils.translation import ugettext as _

class OrganizationForm(forms.ModelForm):
    def save(self, commit=True):
        raise forms.ValidationError("Use api to save")

    class Meta:
        model = Organization
        fields = ['name', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Org name')}),
            'comment': forms.Textarea(attrs={'placeholder': _('Comment')})
        }