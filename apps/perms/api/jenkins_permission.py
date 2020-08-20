#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from orgs.mixins.api import OrgModelViewSet
from common.permissions import IsOrgAdminOrCieUser
from perms.models import CiPermission
from perms.serializers import JenkinsPermissionListSerializer, JenkinsPermissionSerializer,JenkinsPermissionUpdateUserSerializer,JenkinsPermissionUpdateJobSerializer

from rest_framework.response import Response
from rest_framework import status
from orgs.mixins import generics


__all__ = [
    'JenkinsPermissionViewSet',
    'JenkinsPermissionAddUserApi',
    'JenkinsPermissionRemoveUserApi',
    'JenkinsPermissionAddJobApi',
    'JenkinsPermissionRemoveJobApi',
]
class JenkinsPermissionViewSet(OrgModelViewSet):
    model = CiPermission
    filter_fields = ('name', )
    search_fields = filter_fields
    serializer_classes = {
        'default': JenkinsPermissionSerializer,
        'display': JenkinsPermissionListSerializer,
    }
    permission_classes = (IsOrgAdminOrCieUser,)

    def list(self, request, *args, **kwargs):
        return super(JenkinsPermissionViewSet, self).list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class JenkinsPermissionAddUserApi(generics.RetrieveUpdateAPIView):
    model = CiPermission
    permission_classes = (IsOrgAdminOrCieUser,)
    serializer_class = JenkinsPermissionUpdateUserSerializer

    def update(self, request, *args, **kwargs):
        perm = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data.get('users')
            if users:
                perm.users.add(*tuple(users))
            return Response({"msg": "ok"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors})

class JenkinsPermissionRemoveUserApi(generics.RetrieveUpdateAPIView):
    model = CiPermission
    permission_classes = (IsOrgAdminOrCieUser,)
    serializer_class = JenkinsPermissionUpdateUserSerializer

    def update(self, request, *args, **kwargs):
        perm = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            users = serializer.validated_data.get('users')
            if users:
                ret = perm.users.remove(*tuple(users))
            return Response({"msg": "ok"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors})

class JenkinsPermissionAddJobApi(generics.RetrieveUpdateAPIView):
    model = CiPermission
    permission_classes = (IsOrgAdminOrCieUser,)
    serializer_class = JenkinsPermissionUpdateJobSerializer

    def update(self, request, *args, **kwargs):
        perm = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            cis = serializer.validated_data.get('cis')
            print('cis=',request.data)
            if cis:
                perm.cis.add(*tuple(cis))
            return Response({"msg": "ok"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors})

class JenkinsPermissionRemoveJobApi(generics.RetrieveUpdateAPIView):
    model = CiPermission
    permission_classes = (IsOrgAdminOrCieUser,)
    serializer_class = JenkinsPermissionUpdateJobSerializer

    def update(self, request, *args, **kwargs):
        perm = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            cis = serializer.validated_data.get('cis')
            if cis:
                ret = perm.cis.remove(*tuple(cis))
            return Response({"msg": "ok"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors})