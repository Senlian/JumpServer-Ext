# -*- coding: utf-8 -*-
#

from django.urls import re_path, path
from rest_framework.routers import DefaultRouter

from common import api as capi
from .. import api


app_name = 'orgs'
router = DefaultRouter()

# 将会删除
router.register(r'orgs/(?P<org_id>[0-9a-zA-Z\-]{36})/membership/admins',
                api.OrgMembershipAdminsViewSet, 'membership-admins')
router.register(r'orgs/(?P<org_id>[0-9a-zA-Z\-]{36})/membership/users',
                api.OrgMembershipUsersViewSet, 'membership-users'),

router.register(r'orgs', api.OrgViewSet, 'org')
router.register(r'orgs-assets', api.OrgAssetViewSet, 'org-asset')
router.register(r'orgs-users', api.OrgUserViewSet, 'org-user')
router.register(r'orgs-groups', api.OrgUserGroupViewSet, 'org-group')
router.register(r'orgs-domains', api.OrgDomainViewSet, 'org-domain')
router.register(r'orgs-admin-users', api.OrgAdminUserViewSet, 'org-admin-user')
router.register(r'orgs-system-users', api.OrgSystemUserViewSet, 'org-system-user')
router.register(r'orgs-labels', api.OrgLabelViewSet, 'org-lable')

old_version_urlpatterns = [
    re_path('(?P<resource>org)/.*', capi.redirect_plural_name_api)
]

urlpatterns = [
    path('<uuid:pk>/users/all/', api.OrgAllUserListApi.as_view(), name='org-all-users'),
]

urlpatterns += router.urls + old_version_urlpatterns
