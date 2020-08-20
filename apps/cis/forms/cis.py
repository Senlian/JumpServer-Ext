#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext as _
from cis.models import JenkinsCi
from cis.api.mixins import JenkinsApi


class JobCreateModelForm(forms.ModelForm):
    name = forms.CharField(max_length=128,
                           label=_('Name'),
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Project name')}))

    fullname = forms.CharField(max_length=128, required=False,
                               label=_('Full name'),
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Full name')}))

    node = forms.CharField(max_length=128,
                           required=False,
                           empty_value='master',
                           label=_('Node'),
                           widget=forms.TextInput(
                               attrs={'class': 'form-control', 'placeholder': _('Node'), 'value': 'master'}))

    comment = forms.CharField(max_length=200, required=False,
                              label=_('Comment'),
                              widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Comment')}))

    jks = JenkinsApi()

    class Meta:
        model = JenkinsCi
        fields = ['name', 'org_id', 'created_by']

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.jks.job_exists(name):
            raise forms.ValidationError(
                _("Job '{0}' already exists".format(name)),
                code='Job_exists',
            )
        return name

    def save(self, request, config):
        if not request.user:
            return False
        from django.db import transaction
        from orgs.utils import get_current_org_id_for_serializer
        with transaction.atomic():
            self._save_m2m()
            self.instance.org_id = get_current_org_id_for_serializer()
            self.instance.created_by = request.user.name
            self.instance.save()
            self.jks.create_job(self.cleaned_data['name'], config_xml=config)
        return self.instance