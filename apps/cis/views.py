import sys
import base64
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import ProcessFormView, CreateView, FormView, ModelFormMixin
from django.utils.translation import ugettext as _
from jenkins import Jenkins, EMPTY_FOLDER_XML
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.http import unquote

# from django.contrib.messages.views import SuccessMessageMixin
from common.permissions import PermissionsMixin, IsOrgAdmin, IsValidUser, IsOrgAdminOrCieUser
from cis import forms
from cis.api import JenkinsApi
# from collections import OrderedDict

# Create your views here.
# API documents: https://python-jenkins.readthedocs.io/en/latest/examples.html

EMPTY_CONFIG_XML = '''<?xml version='1.0' encoding='UTF-8'?>
<project>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class='cis.scm.NullSCM'/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>
    <hudson.triggers.TimerTrigger>
      <spec>H/30 * * * *</spec>
    </hudson.triggers.TimerTrigger>
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>'''

__all__ = [
    "JenkinsView",
    "JenkinsCreateView",
    "JenkinsUpdateView",
    "JenkinsLogView",
    "JenkinsPlayView",
]


class JenkinsView(PermissionsMixin, TemplateView):
    template_name = 'cis/jenkins.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Jenkins'),
            'action': _('Projects'),
            'JMS_TITLE': _('Jenkins-Jumpserver'),
            'messages': ["Jenkins是单独部署的一个第三方程序，请确保服务端已经正确部署和配置！"]
        })
        return context

class JenkinsNodeView(PermissionsMixin, TemplateView):
    template_name = 'cis/jenkins_node_list.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Jenkins'),
            'action': _('Projects'),
            'JMS_TITLE': _('Jenkins-Jumpserver'),
            'messages': ["该功能尚待升级，暂时只能展示节点！"]
        })
        return context

class JenkinsCreateView(PermissionsMixin, FormView):
    template_name = 'cis/jenkins_create_update.html'
    form_class = forms.JobCreateModelForm
    permission_classes = [IsOrgAdminOrCieUser]
    success_url = reverse_lazy("cis:ci-list")

    def form_invalid(self, form):
        return super(JenkinsCreateView, self).form_invalid(form)

    def form_valid(self, form):
        if form.is_valid():
            form.save(request=self.request, config=EMPTY_CONFIG_XML)
        return super(JenkinsCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Jenkins'),
            'action': _('Create project'),
            "type": "create"
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class JenkinsUpdateView(TemplateView):
    template_name = 'cis/jenkins.html'

    @property
    def jk(self):
        return Jenkins(settings.JENKINS_URL, username=settings.JENKINS_USERNAME, password=settings.JENKINS_PASSWORD)

    def get(self, request, *args, **kwargs):
        # return super(JenkinsUpdateView, self).get(request, *args, **kwargs)
        # from django.http.response import HttpResponseRedirect
        # from urllib.parse import urljoin
        job_name = kwargs.get('job_name')
        if job_name:
            config = self.jk.get_job_config(job_name)
        # return HttpResponseRedirect(urljoin(settings.JENKINS_URL, 'job/'+job_name+'/configure'))
        return super(JenkinsUpdateView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Jenkins'),
            'action': _('Update job'),
            'type': 'update'
        })
        return context


class JenkinsLogView(PermissionsMixin, TemplateView):
    template_name = 'cis/jenkins_job_log.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'app': _('Jenkins'),
            'app_url': unquote(reverse_lazy("cis:ci-list")),
            'action': _('Job logs'),
            'JMS_TITLE': _('Jenkins-Jumpserver'),
        })
        return context


# 该视图生成参数页面，暂未使用
class JenkinsPlayView(PermissionsMixin, TemplateView):
    template_name = 'cis/jenkins_job_play.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        jksApi = JenkinsApi()
        jobName = unquote(base64.b64decode(kwargs.get('job_name')).decode('utf-8'))
        parameters, referencedDict = jksApi.get_job_parameters(jobName)
        context = {
            'app': _('Jenkins'),
            'action': _('Create project'),
            'parameters': parameters,
            'referencedDict': referencedDict,
            'job_name': jobName,
            'JMS_TITLE': _('Jenkins-Jumpserver'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
