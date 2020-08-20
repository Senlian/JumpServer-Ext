#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from rest_framework import serializers

from common.fields import StringManyToManyField
from common.serializers import AdaptedBulkListSerializer
from orgs.mixins.serializers import BulkOrgResourceModelSerializer
from perms.models import CiPermission

# BulkOrgResourceModelSerializer自动添加org_id字段 ，默认是获取当前org_id
class JenkinsPermissionListSerializer(BulkOrgResourceModelSerializer):
    users = StringManyToManyField(many=True, read_only=True)
    user_groups = StringManyToManyField(many=True, read_only=True)
    jenkins = StringManyToManyField(many=True, read_only=True, source='cis')
    nodes = StringManyToManyField(many=True, read_only=True)
    is_valid = serializers.BooleanField()
    is_expired = serializers.BooleanField()

    class Meta:
        model = CiPermission
        fields = '__all__'

class JenkinsPermissionListCisSerializer(serializers.ModelSerializer):
    cis = StringManyToManyField(many=True, read_only=True)
    class Meta:
        model = CiPermission
        fields = ['cis']

class JenkinsPermissionSerializer(BulkOrgResourceModelSerializer):
    class Meta:
        model = CiPermission
        list_serializer_class = AdaptedBulkListSerializer
        fields = [
            'id', 'name', 'users', 'user_groups', 'cis', 'comment',
            'is_active', 'date_start', 'date_expired', 'is_valid',
            'created_by', 'date_created',
        ]
        read_only_fields = ['created_by', 'date_created']

class JenkinsPermissionUpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiPermission
        fields = ['id', 'users']

class JenkinsPermissionUpdateJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CiPermission
        fields = ['id', 'cis']