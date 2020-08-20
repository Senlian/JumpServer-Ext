from __future__ import absolute_import

from django.urls import path

from .. import api
from cis.api import JenkinsViewSet
app_name = 'common'

urlpatterns = [
    path('mail/testing/', api.MailTestingAPI.as_view(), name='mail-testing'),
    path('jenkins/testing/', JenkinsViewSet.as_view({'post': 'test_connect'}), name='jenkins-testing'),
    path('ldap/testing/config/', api.LDAPTestingConfigAPI.as_view(), name='ldap-testing-config'),
    path('ldap/testing/login/', api.LDAPTestingLoginAPI.as_view(), name='ldap-testing-login'),
    path('ldap/users/', api.LDAPUserListApi.as_view(), name='ldap-user-list'),
    path('ldap/users/import/', api.LDAPUserImportAPI.as_view(), name='ldap-user-import'),
    path('ldap/cache/refresh/', api.LDAPCacheRefreshAPI.as_view(), name='ldap-cache-refresh'),

    path('public/', api.PublicSettingApi.as_view(), name='public-setting'),
]
