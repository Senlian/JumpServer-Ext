from django.shortcuts import redirect, reverse
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.views.generic import View, TemplateView, ListView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin

from .models import Organization
from assets.models import Asset
from common.utils import UUID_PATTERN
from common.const import create_success_msg, update_success_msg
from common.permissions import PermissionsMixin, IsOrgAdmin, IsValidUser
from . import forms


class SwitchOrgView(DetailView):
    model = Organization
    object = None

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        self.object = Organization.get_instance(pk)
        oid = str(self.object.id)
        request.session['oid'] = oid
        org_change_to_url = settings.ORG_CHANGE_TO_URL
        if org_change_to_url:
            return redirect(org_change_to_url)
        host = request.get_host()
        referer = request.META.get('HTTP_REFERER', '')
        if referer.find(host) == -1:
            return redirect(reverse('index'))
        if UUID_PATTERN.search(referer):
            return redirect(reverse('index'))
        # 组织管理员切换到组织审计员时(403)
        if not self.object.get_org_admins().filter(id=request.user.id):
            return redirect(reverse('index'))
        return redirect(referer)


class SwitchToAOrgView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_common_user:
            return HttpResponseForbidden()
        admin_orgs = request.user.admin_orgs
        audit_orgs = request.user.audit_orgs
        default_org = Organization.default()
        if admin_orgs:
            if default_org in admin_orgs:
                redirect_org = default_org
            else:
                redirect_org = admin_orgs[0]
            return redirect(reverse('orgs:org-switch', kwargs={'pk': redirect_org.id}))
        if audit_orgs:
            if default_org in audit_orgs:
                redirect_org = default_org
            else:
                redirect_org = audit_orgs[0]
            return redirect(reverse('orgs:org-switch', kwargs={'pk': redirect_org.id}))


class OrgListView(TemplateView):
    template_name = 'orgs/org_list.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Org list')
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)



class OrgCreateView(PermissionsMixin, SuccessMessageMixin, CreateView):
    model = Organization
    form_class = forms.OrganizationForm
    template_name = 'orgs/org_create_update.html'
    success_url = reverse_lazy('orgs:org-list')
    success_message = create_success_msg
    permission_classes = [IsOrgAdmin]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Create Organization'),
            "type": "create"
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class OrgDetailView(PermissionsMixin, DetailView):
    model = Organization
    context_object_name = 'org'
    template_name = 'orgs/org_detail.html'
    permission_classes = [IsValidUser]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Org detail'),
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class OrgUpdateView(PermissionsMixin, SuccessMessageMixin, UpdateView):
    model = Organization
    form_class = forms.OrganizationForm
    template_name = 'orgs/org_create_update.html'
    success_url = reverse_lazy('orgs:org-list')
    success_message = update_success_msg
    permission_classes = [IsOrgAdmin]

    def get_context_data(self, **kwargs):
        context = {
            'app': _('XPack'),
            'action': _('Update org'),
            "type": "update"
        }
        kwargs.update(context)
        return super().get_context_data(**kwargs)


class OrgAssetsView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_assets.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Orgs assets'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)


class OrgUsersView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_users.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Orgs users'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)


class OrgGroupsView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_groups.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Orgs groups'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)


class OrgDomainsView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_domain.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Domain list'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)

class OrgAdminUsersView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_admin_user.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Admin user list'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)

class OrgSystemUsersView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_system_user.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('System user list'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)

class OrgLabelsView(PermissionsMixin, SingleObjectMixin, ListView):
    paginate_by = settings.DISPLAY_PER_PAGE
    template_name = 'orgs/org_labels.html'
    context_object_name = 'org'
    object = None
    permission_classes = [IsValidUser]

    def get(self, request, *args, **kwargs):
        # 查出属于该组织的资产列表
        self.object = self.get_object(queryset=Organization.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = Asset.objects.set_current_org(self.object.id).all()
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = {
            'app': _('Organizations'),
            'action': _('Label list'),
            'org_assets': self.queryset
        }
        kwargs.update(context)
        # ListView类的get_context_data方法将self.queryset赋值给context_object_name对象
        return super().get_context_data(**kwargs)
