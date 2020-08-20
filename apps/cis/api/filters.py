#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import coreapi
import operator
from functools import reduce
from django.db import models
from django.utils import six
from django.core.cache import cache
from rest_framework import filters

from common import const
from perms.serializers import JenkinsPermissionListCisSerializer

class JenkinsJobFilterBackend(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = self.get_search_fields(view, request)
        search_terms = self.get_search_terms(request)
        if not search_fields or not search_terms:
            return queryset

        orm_lookups = [
            self.construct_search(six.text_type(search_field))
            for search_field in search_fields
        ]

        conditions = []
        for search_term in search_terms:
            queries = [
                models.Q(**{orm_lookup: search_term})
                for orm_lookup in orm_lookups
            ]
            conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))
        return queryset


class JobNameSpmFilter(filters.BaseFilterBackend):
    def get_schema_fields(self, view):
        return [
            coreapi.Field(
                name='spm', location='query', required=False,
                type='string', example='',
                description='Pre post objects id get spm id, then using filter'
            )
        ]

    def filter_queryset(self, request, queryset, view):
        spm = request.query_params.get('spm')
        if not spm:
            return queryset
        # 缓存获取要删除的字段值，此处在ajax提交请求前将字段存入缓存，传递缓存spm值给后端，后端根据spm从缓存获取
        cache_key = const.KEY_CACHE_RESOURCES_ID.format(spm)
        job_names = cache.get(cache_key)
        if not job_names or not isinstance(job_names, list):
            return queryset
        conditions = []
        queries = [models.Q(**{'name__eq': name}) for name in job_names]
        conditions.append(reduce(operator.or_, queries))
        queryset = queryset.filter(reduce(operator.and_, conditions))
        return queryset


class JenkinsJobUserFilter(filters.SearchFilter):
    def filter_queryset(self, request, queryset, view):
        serializer = JenkinsPermissionListCisSerializer(instance=request.user.cipermission_set.all(), many=True)
        jobs = [filed.get('cis') for filed in serializer.data]
        jobs = jobs if not jobs else jobs[0]
        return [job for job in queryset if job.get('name') in jobs]