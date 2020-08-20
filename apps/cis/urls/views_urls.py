#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from django.urls import path, re_path
from .. import views

app_name = 'cis'

urlpatterns = [
    path('', views.JenkinsView.as_view(), name='cis'),
    path('ci/', views.JenkinsView.as_view(), name='ci-list'),
    path('ci/<str:job_name>/play', views.JenkinsPlayView.as_view(), name='ci-play'),
    path('ci/create/', views.JenkinsCreateView.as_view(), name='ci-create'),
    path('ci/<str:job_name>/udpate', views.JenkinsUpdateView.as_view(), name='ci-udpate'),
    path('ci/<str:job_name>/<int:version>/log', views.JenkinsLogView.as_view(), name='ci-log'),
    path('nodes/', views.JenkinsNodeView.as_view(), name='ci-nodes'),
]
