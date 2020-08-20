# coding:utf-8
from django.urls import path, re_path
from rest_framework_nested import routers
# from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter, SimpleRouter

from common import api as capi

from .. import api

app_name = 'cis'

router = BulkRouter()

router.register(r'cis', api.JenkinsViewSet, basename='ci')

urlpatterns = [
    path('cis/<str:name>/<int:version>/log', api.JenkinsViewSet.as_view({'get': 'log'}), name='ci-log'),
]
urlpatterns += router.urls
