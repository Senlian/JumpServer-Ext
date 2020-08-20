# coding: utf-8
#

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from .base import BaseForm
# from settings.models import Setting
from django.core.cache import cache
__all__ = ['JenkinsSettingForm']


class JenkinsSettingForm(BaseForm):
    JENKINS_URL = forms.URLField(
        label=_("Jenkins Site Url"),
        # initial=settings.JENKINS_URL,
        help_text=_("Tips: Jenkins Site Url")
    )
    JENKINS_USERNAME = forms.CharField(
        max_length=1024, label=_("Username"),
        # initial=settings.JENKINS_USERNAME,
        help_text=_("Tips: Jenkins administrator")
    )

    # default_password = Setting.objects.filter(name='JENKINS_PASSWORD')
    default_password = cache.get('_SETTING_JENKINS_PASSWORD')
    # default_password = settings.JENKINS_PASSWORD if not bool(default_password) else default_password.first().get('JENKINS_PASSWORD')
    default_password = settings.JENKINS_PASSWORD if not bool(default_password) else default_password
    JENKINS_PASSWORD = forms.CharField(
        max_length=1024, label=_("Password"), widget=forms.PasswordInput(render_value=default_password),
        help_text=_("Tips: Jenkins management password")
    )
