#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import base64
from urllib.parse import unquote

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.filters import OrderingFilter

from orgs.utils import get_current_org_id
from common.permissions import IsOrgAdminOrCieUser, IsValidUser
from orgs.mixins.api import OrgBulkModelViewSet
from cis.api.mixins import JenkinsApi, JobList
from cis.api.serializer import JenkinsJobSerializer, JenkinsNodeSerializer
from cis.api.filters import JenkinsJobFilterBackend, JobNameSpmFilter, JenkinsJobUserFilter

from cis.models import JenkinsCi


class JenkinsViewSet(OrgBulkModelViewSet):
    # url传参字段
    lookup_field = 'name'
    # 用于搜索
    search_fields = ("name", "status", "label",)
    # 权限
    permission_classes = (IsOrgAdminOrCieUser,)
    # 排序字段
    ordering_fields = ("name", "status", "label",)
    # 序列化获取字段
    serializer_class = JenkinsJobSerializer
    # 过滤器
    filter_backends = [DjangoFilterBackend, OrderingFilter, JenkinsJobFilterBackend]
    default_added_filters = [JobNameSpmFilter]
    model = JenkinsCi
    InitDB = True

    @property
    def queryApi(self):
        return JenkinsApi(db=self.InitDB)

    def get_permissions(self):
        permissions = super(JenkinsViewSet, self).get_permissions()
        if self.request.COOKIES.get('IN_ADMIN_PAGE') == 'No':
            permissions = (IsValidUser(),)
        return permissions

    def get_filter_backends(self):
        filter_backends = super(JenkinsViewSet, self).get_filter_backends()
        if self.request.COOKIES.get('IN_ADMIN_PAGE') == 'No':
            filter_backends.append(JenkinsJobUserFilter)
        return filter_backends

    # 此处在ExtraFilterFieldsMixin的filter_queryset中调用了filter_backends
    def filter_queryset(self, queryset):
        return super(JenkinsViewSet, self).filter_queryset(queryset)

    def get_queryset(self):
        queryset = self.model.objects.values_list('name', flat=True)
        return self.queryApi(jobs_in_db=queryset)

    # method=GET
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            # many=True 表示处理list类型数据
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        value = self.kwargs.get(lookup_url_kwarg)
        queryset = self.filter_queryset(self.get_queryset())
        # 将queryset转换为符合条件的JobList对象
        instance = JobList(jks=queryset.jks)
        [instance.append(job) for job in queryset if job.get(lookup_url_kwarg) == value]
        return instance

    # 定义允许批量删除的条件, method=DELETE
    def allow_bulk_destroy(self, qs, filtered):
        return filtered.issubset(qs)

    # 定义批量删除中间步骤
    def perform_bulk_destroy(self, objects):
        self.perform_destroy(objects)

    def partial_bulk_update(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for job in (json.loads(request._request.body)):
            is_active = job.get('is_active')
            if is_active:
                queryset.enable_job(job)
            else:
                queryset.disable_job(job)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True)
    def args(self, request, *args, **kwargs):
        '''
        :param request:
        :param args:
        :param kwargs:
        :return: 返回任务的所有参数
        '''
        self.InitDB = False
        jobName = kwargs.get('name')
        jobName = unquote(base64.b64decode(jobName).decode('utf-8'))
        if not jobName:
            return Response(status=status.HTTP_417_EXPECTATION_FAILED)
        else:
            try:
                parameters, referencedDict = self.queryApi.get_job_parameters(jobName)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_417_EXPECTATION_FAILED)
        if not parameters:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'args': parameters, 'reference': referencedDict})

    @action(methods=['post'], detail=True)
    def build(self, request, *args, **kwargs):
        '''
            说明： 仅接收POST方法
            功能： 任务创建
        '''
        self.InitDB = False
        args = request.data
        parameters = args if isinstance(args, dict) else {}
        if not parameters:
            for arg in args:
                if isinstance(arg, dict):
                    if not parameters:
                        parameters = arg
                    else:
                        parameters.update(arg)
        job_name = base64.b64decode(kwargs.get('name')).decode('utf-8') or parameters.pop('jenkins_job_name')
        job_name = unquote(job_name)
        if 'jenkins_job_name' in parameters:
            parameters.pop('jenkins_job_name')

        job_number = self.queryApi.build_job(job_name, parameters)
        return Response(data={'job_number': job_number}, status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def groovy(self, request, *args, **kwargs):
        '''
            说明： 仅接收POST方法
            功能： 执行脚本
        '''
        self.InitDB = False
        itemParameter = request.data.get('itemParameter')
        scriptArgs = request.data.get('scriptArgs', {})
        # print(json.dumps(request.data,indent=2))
        secureScript = itemParameter.get('secureScript')
        secureFallbackScript = itemParameter.get('secureFallbackScript')
        try:
            choices = self.queryApi.run_script(secureScript.format(**scriptArgs))
        except Exception as e:
            choices = self.queryApi.run_script(secureFallbackScript.format(**scriptArgs))
        itemParameter['choices'] = choices
        itemParameter['defaultValue'] = '' if not choices else choices[0]

        # print(self.queryApi.get_build_info('Job1',self.queryApi.get_running_builds()[-1].get('number')))

        # print(self.queryApi.get_build_console_output('Job1',self.queryApi.get_running_builds()[-1].get('number')))
        return Response({'arg_info': itemParameter})

    @action(methods=['get'], detail=True)
    def stop(self, request, *args, **kwargs):
        '''
            说明： 仅接收POST方法
            功能： 执行脚本
        '''
        self.InitDB = False
        jobName = base64.b64decode(kwargs.get('name')).decode('utf-8')
        jobName = unquote(jobName)
        buildNumber = self.queryApi.get_job_info(jobName).get('nextBuildNumber', 1) - 1
        if buildNumber:
            self.queryApi.stop_build(jobName, buildNumber)
            return Response({'number': buildNumber}, status=status.HTTP_200_OK)
        else:
            Response({'number': buildNumber}, status=status.HTTP_417_EXPECTATION_FAILED)

    def log(self, request, *args, **kwargs):
        '''
            说明： 仅接收POST方法
            功能： 执行脚本
        '''
        self.InitDB = False
        jobName = kwargs.get('name')
        version = int(kwargs.get('version'))
        # B64解码
        jobName = unquote(base64.b64decode(jobName).decode('utf-8'))
        # buildNumber = self.queryApi.get_job_info(jobName).get('nextBuildNumber', 1) - 1
        try:
            console_output = self.queryApi.get_build_console_output(jobName, version)
        except Exception as e:
            print(e)
            console_output = 'No records!!!'
        if version:
            return Response({'console_output': console_output}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], url_path='nodes', url_name='nodes', basename='ci', detail=False)
    def nodes(self, request, *args, **kwargs):
        self.serializer_class = JenkinsNodeSerializer
        # self.ordering_fields = ("name", "offline", )
        try:
            queryset = self.queryApi.get_nodes()
            # page = self.paginate_queryset(queryset)
            # if page is not None:
            #     serializer = self.get_serializer(instance=page, many=True)
            #     return self.get_paginated_response(serializer.data)
            # serializer = self.get_serializer(instance=queryset, many=True)
            # return Response(serializer.data)
        except Exception as e:
            queryset = []
            # error = e.args[0] if isinstance(e.args[0], str) else e.args[0].args[0]
            # return Response(data={'error': error}, status=status.HTTP_401_UNAUTHORIZED)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)

    def test_connect(self, request, *args, **kwargs):
        formData = request.data
        url = formData.get('JENKINS_URL')
        username = formData.get('JENKINS_USERNAME')
        password = formData.get('JENKINS_PASSWORD')
        api = JenkinsApi(url=url, username=username, password=password, db=False)
        # from django.core.exceptions import Max
        try:
            me = api.get_whoami()
            return Response({'msg': '[' + me.get('fullName') + ']测试连接成功！'})
        except Exception as e:
            error = e.args[0] if isinstance(e.args[0], str) else e.args[0].args[0]
            return Response(data={'error': error}, status=401)
