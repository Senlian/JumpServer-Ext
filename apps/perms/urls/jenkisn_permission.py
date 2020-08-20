#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path
from rest_framework_bulk.routes import BulkRouter
from .. import api


router = BulkRouter()
router.register('jenkins-permissions', api.JenkinsPermissionViewSet, 'jenkins-permission')

jenkins_permission_urlpatterns = [
    path('jenkins-permissions/<uuid:pk>/users/add/', api.JenkinsPermissionAddUserApi.as_view(), name='jenkins-permission-add-user'),
    path('jenkins-permissions/<uuid:pk>/users/remove/', api.JenkinsPermissionRemoveUserApi.as_view(), name='jenkins-permission-remove-user'),
    path('jenkins-permissions/<uuid:pk>/jobs/add/', api.JenkinsPermissionAddJobApi.as_view(), name='jenkins-permission-add-job'),
    path('jenkins-permissions/<uuid:pk>/jobs/remove/', api.JenkinsPermissionRemoveJobApi.as_view(), name='jenkins-permission-remove-job'),
]
jenkins_permission_urlpatterns += router.urls