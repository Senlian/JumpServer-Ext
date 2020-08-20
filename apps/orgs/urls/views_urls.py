# -*- coding: utf-8 -*-
#

from django.urls import path

from .. import views

app_name = 'orgs'


urlpatterns = [
    path('<str:pk>/switch/', views.SwitchOrgView.as_view(), name='org-switch'),
    path('switch-a-org/', views.SwitchToAOrgView.as_view(), name='switch-a-org'),
    path('org/', views.OrgListView.as_view(), name='org-list'),
    path('org/create/', views.OrgCreateView.as_view(), name='org-create'),
    path('org/<uuid:pk>/', views.OrgDetailView.as_view(), name='org-detail'),
    path('org/<uuid:pk>/update/', views.OrgUpdateView.as_view(), name='org-update'),
    path('org/<uuid:pk>/assets/', views.OrgAssetsView.as_view(), name='org-assets'),
    path('org/<uuid:pk>/users/', views.OrgUsersView.as_view(), name='org-users'),
    path('org/<uuid:pk>/groups/', views.OrgGroupsView.as_view(), name='org-groups'),
    path('org/<uuid:pk>/domains/', views.OrgDomainsView.as_view(), name='org-domains'),
    path('org/<uuid:pk>/admin-user/', views.OrgAdminUsersView.as_view(), name='org-admin-users'),
    path('org/<uuid:pk>/system-user/', views.OrgSystemUsersView.as_view(), name='org-system-users'),
    path('org/<uuid:pk>/label/', views.OrgLabelsView.as_view(), name='org-labels'),
]
