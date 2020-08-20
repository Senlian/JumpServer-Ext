#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, ListView
from django.views.generic.edit import SingleObjectMixin
from django.utils.translation import ugettext as _
from django.urls import reverse_lazy
from django.utils.http import unquote
from django.conf import settings

from common.permissions import PermissionsMixin, IsOrgAdminOrCieUser, IsOrgCie
from perms.models.ci_permission import CiPermission
from perms.forms import JenkinsPermissionCreateUpdateForm
from users.models import UserGroup
from orgs.utils import current_org
from cis.models import JenkinsCi

__all__ = [
    'JenkinsPermissionListView',
    'JenkinsPermissionDetailView',
    'JenkinsPermissionCreateView',
    'JenkinsPermissionUpdateView',
    'JenkinsPermissionUserView',
    'JenkinsPermissionJobView',
]


class JenkinsPermissionListView(PermissionsMixin, TemplateView):
    template_name = 'perms/jenkins_permission_list.html'
    permission_classes = [IsOrgAdminOrCieUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Perms'),
            'action': _('Jenkins permission list'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class JenkinsPermissionDetailView(PermissionsMixin, DetailView):
    template_name = 'perms/jenkins_permission_detail.html'
    model = CiPermission
    permission_classes = [IsOrgAdminOrCieUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Perms'),
            'app_url': unquote(reverse_lazy("perms:jenkins-permission-list")),
            'action': _('Jenkins permission detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class JenkinsPermissionCreateView(PermissionsMixin, CreateView):
    template_name = 'perms/jenkins_permission_create_update.html'
    model = CiPermission
    form_class = JenkinsPermissionCreateUpdateForm
    success_url = reverse_lazy('perms:jenkins-permission-list')
    permission_classes = [IsOrgAdminOrCieUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Perms'),
            'app_url': unquote(reverse_lazy("perms:jenkins-permission-list")),
            'action': _('Create jenkins permission'),
            'api_action': 'create'
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class JenkinsPermissionUpdateView(PermissionsMixin, UpdateView):
    template_name = 'perms/jenkins_permission_create_update.html'
    model = CiPermission
    form_class = JenkinsPermissionCreateUpdateForm
    success_url = reverse_lazy('perms:jenkins-permission-list')
    permission_classes = [IsOrgAdminOrCieUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Perms'),
            'app_url': unquote(reverse_lazy("perms:jenkins-permission-list")),
            'action': _('Update jenkins permission'),
            'api_action': 'update'
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class JenkinsPermissionUserView(PermissionsMixin,
                                SingleObjectMixin,
                                ListView):
    template_name = 'perms/jenkins_permission_user.html'
    context_object_name = 'jenkins_permission'
    paginate_by = settings.DISPLAY_PER_PAGE
    object = None
    permission_classes = [IsOrgAdminOrCieUser]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=CiPermission.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = list(self.object.get_all_users())
        return queryset

    def get_context_data(self, **kwargs):
        users = [str(i) for i in self.object.users.all().values_list('id', flat=True)]
        user_remain = current_org.get_org_members(exclude=('Auditor',)).exclude(cipermission=self.object)
        user_groups_remain = UserGroup.objects.exclude(
            cipermission=self.object)
        context = {
            'app': _('Perms'),
            'app_url': unquote(reverse_lazy("perms:jenkins-permission-list")),
            'action': _('Jenkins permission user list'),
            'users': users,
            'users_remain': user_remain,
            'user_groups_remain': user_groups_remain,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)

class JenkinsPermissionJobView(PermissionsMixin,
                                SingleObjectMixin,
                                ListView):
    template_name = 'perms/jenkins_permission_job.html'
    context_object_name = 'jenkins_permission'
    paginate_by = settings.DISPLAY_PER_PAGE
    object = None
    permission_classes = [IsOrgAdminOrCieUser]

    def get(self, request, *args, **kwargs):
        # 权限
        self.object = self.get_object(queryset=CiPermission.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # 权限管理ci
        queryset = list(self.object.get_all_cis())
        return queryset

    def get_context_data(self, **kwargs):
        jenkins_granted = self.get_queryset()
        jenkins_remain = JenkinsCi.objects.exclude(
            id__in=[a.id for a in jenkins_granted])

        context = {
            'app': _('Perms'),
            'app_url': unquote(reverse_lazy("perms:jenkins-permission-list")),
            'action': _('Jenkins related tasks'),
            'jenkins_remain': jenkins_remain,
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)
