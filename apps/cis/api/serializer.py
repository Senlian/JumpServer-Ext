#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.utils.http import unquote, quote
from rest_framework import serializers
from rest_framework.fields import empty
from django.utils.translation import ugettext as _
from django.urls import reverse
from urllib.parse import urljoin
import base64


class JenkinsJobSerializer(serializers.Serializer):
    job_type = serializers.CharField(source='_class')
    # 需要ID，否则多选框无用
    id = serializers.CharField(source='name')
    name = serializers.CharField()
    version = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    url_set = serializers.SerializerMethodField()
    color = serializers.CharField()
    fullname = serializers.CharField()
    status = serializers.SerializerMethodField()
    label = serializers.CharField()

    def __init__(self, instance=None, data=empty, **kwargs):
        super(JenkinsJobSerializer, self).__init__(instance=instance, data=data, **kwargs)

    def get_version(self, row):
        # b64编码 解决url带\的问题
        version = int(row.get('nextBuildNumber', 1)) - 1
        return '#' + str(version)

    def get_url(self, row):
        # b64编码 解决url带\的问题
        job_name = base64.b64encode(row.get('name').encode('utf-8')).decode('utf-8')
        version = int(row.get('nextBuildNumber', 1)) - 1
        return unquote(reverse('cis:ci-log', kwargs={'job_name': job_name, 'version': version}))

    def get_url_set(self, row):
        # b64编码 解决url带\的问题
        job_url = unquote(row.get('url'))
        return unquote(urljoin(job_url, 'configure'))

    def get_status(self, row):
        return _(unquote(row.get('status')))

class JenkinsNodeSerializer(serializers.Serializer):
    name = serializers.CharField()
    offline = serializers.BooleanField()
