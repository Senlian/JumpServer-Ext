# -*- coding: utf-8 -*-
#

from django.shortcuts import get_object_or_404
from rest_framework import status, generics, filters
from rest_framework.views import Response
from rest_framework_bulk import BulkModelViewSet

from common.permissions import IsSuperUserOrAppUser, NeedMFAVerify, IsValidUser
from .models import Organization
from .serializers import OrgSerializer, OrgReadSerializer, \
    OrgMembershipUserSerializer, OrgMembershipAdminSerializer, \
    OrgAllUserSerializer
from users.models import User, UserGroup
from users.serializers import UserDisplaySerializer, UserGroupSerializer
from assets.models import Asset, Domain, AdminUser, SystemUser, Label
from assets.serializers import DomainSerializer, AdminUserSerializer
from assets.api import AdminUserViewSet, SystemUserViewSet, LabelViewSet

from perms.models import AssetPermission
from orgs.utils import current_org
from common.utils import get_logger, get_object_or_none
from .mixins.api import OrgMembershipModelViewSetMixin
from .utils import set_current_org, get_current_org
from assets.serializers import AssetUserWriteSerializer, AssetUserReadSerializer, AssetUserReadSerializer
from assets.api.asset_user import AssetUserFilterBackend, AssetUserSearchBackend, AssetUserLatestFilterBackend
from assets.backends import AssetUserManager
from common.mixins import CommonApiMixin

logger = get_logger(__file__)


class OrgViewSet(BulkModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrgSerializer
    permission_classes = (IsSuperUserOrAppUser,)
    search_fields = ("name", "created_by", "date_created")
    org = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return OrgReadSerializer
        else:
            return super().get_serializer_class()

    def get_data_from_model(self, model):
        if model == User:
            data = model.objects.filter(related_user_orgs__id=self.org.id)
        else:
            data = model.objects.filter(org_id=self.org.id)
        return data

    def destroy(self, request, *args, **kwargs):
        self.org = self.get_object()
        models = [
            User, UserGroup,
            Asset, Domain, AdminUser, SystemUser, Label,
            AssetPermission,
        ]
        for model in models:
            data = self.get_data_from_model(model)
            # data.delete()
            # data = self.get_data_from_model(model)
            if data:
                return Response({'msg': True, 'error': '存在关联数据'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if str(current_org) == str(self.org):
                return Response({'msg': True, 'error': '组织不可删除组织自身'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            self.org.delete()
            return Response({'msg': True}, status=status.HTTP_200_OK)


class OrgMembershipAdminsViewSet(OrgMembershipModelViewSetMixin, BulkModelViewSet):
    serializer_class = OrgMembershipAdminSerializer
    membership_class = Organization.admins.through
    permission_classes = (IsSuperUserOrAppUser,)


class OrgMembershipUsersViewSet(OrgMembershipModelViewSetMixin, BulkModelViewSet):
    serializer_class = OrgMembershipUserSerializer
    membership_class = Organization.users.through
    permission_classes = (IsSuperUserOrAppUser,)


class OrgAllUserListApi(generics.ListAPIView):
    permission_classes = (IsSuperUserOrAppUser,)
    serializer_class = OrgAllUserSerializer
    filter_fields = ("username", "name")
    search_fields = filter_fields

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        org = get_object_or_404(Organization, pk=pk)
        users = org.get_org_users().only(*self.serializer_class.Meta.only_fields)
        return users


class OrgUserFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        for field in view.filter_fields:
            value = request.GET.get(field)
            if not value:
                continue
            if field == "org_id":
                users = Organization.users.through.objects.filter(organization_id=value)
                queryset = queryset.filter(id__in=[user.user_id for user in users])
                continue
            kwargs[field] = value
        if kwargs:
            queryset = queryset.filter(**kwargs)
        logger.debug("Filter {}".format(kwargs))
        return queryset


class OrgAssetViewSet(CommonApiMixin, BulkModelViewSet):
    serializer_classes = {
        'default': AssetUserWriteSerializer,
        'list': AssetUserReadSerializer,
        'retrieve': AssetUserReadSerializer,
    }
    permission_classes = [IsValidUser]
    filter_fields = [
        "id", "ip", "hostname", "username",
        "asset_id", "node_id", "prefer", "prefer_id",
    ]
    search_fields = ["ip", "hostname", "username"]
    filter_backends = [
        AssetUserFilterBackend,
        AssetUserSearchBackend,
        AssetUserLatestFilterBackend,
    ]

    def allow_bulk_destroy(self, qs, filtered):
        return False

    def get_object(self):
        pk = self.kwargs.get("pk")
        queryset = self.get_queryset()
        obj = queryset.get(id=pk)
        return obj

    def get_exception_handler(self):
        def handler(e, context):
            return Response({"error": str(e)}, status=400)

        return handler

    def perform_destroy(self, instance):
        manager = AssetUserManager()
        manager.delete(instance)

    def get_queryset(self):
        manager = AssetUserManager()
        queryset = manager.all()
        return queryset


class OrgUserViewSet(BulkModelViewSet):
    model = User
    serializer_class = UserDisplaySerializer
    filter_fields = ("username", "name", 'org_id')
    filter_backends = [OrgUserFilterBackend]

    def get_queryset(self):
        return self.model.objects.all()


class OrgUserGroupFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        kwargs = {}
        for field in view.filter_fields:
            value = request.GET.get(field)
            if not value:
                continue
            kwargs[field] = value
        if kwargs:
            queryset = queryset.filter(**kwargs)
        logger.debug("Filter {}".format(kwargs))
        return queryset


class OrgUserGroupViewSet(BulkModelViewSet):
    model = UserGroup
    serializer_class = UserGroupSerializer
    filter_fields = ("name", "org_id")
    filter_backends = [OrgUserGroupFilterBackend]

    def get_queryset(self):
        queryset = self.model.objects.set_current_org(Organization.root()).all()
        return queryset


class OrgDomainViewSet(BulkModelViewSet):
    model = Domain
    serializer_class = DomainSerializer
    filter_fields = ("name", "org_id")
    filter_backends = [OrgUserGroupFilterBackend]

    def get_queryset(self):
        queryset = self.model.objects.set_current_org(Organization.root()).all()
        return queryset


class OrgAdminUserViewSet(AdminUserViewSet):
    filter_fields = ("name", "org_id")

    def get_queryset(self):
        queryset = self.model.objects.set_current_org(Organization.root()).all()
        return queryset


class OrgSystemUserViewSet(SystemUserViewSet):
    filter_fields = ("name", "username", "org_id")

    def get_queryset(self):
        queryset = self.model.objects.set_current_org(Organization.root()).all()
        return queryset


class OrgLabelViewSet(LabelViewSet):
    filter_fields = ("name", "value", "org_id")

    def get_queryset(self):
        self.queryset = self.model.objects.set_current_org(Organization.root()).all()
        return super().get_queryset()
