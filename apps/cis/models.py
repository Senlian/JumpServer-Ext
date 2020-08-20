from django.db import models
from orgs.mixins.models import OrgModelMixin
from common.mixins.models import CommonModelMixin
from django.utils.translation import ugettext as _


# Create your models here.

class JenkinsCi(CommonModelMixin, OrgModelMixin):
    name = models.CharField(max_length=60, verbose_name='工程名', unique=True)
    comment = models.TextField(blank=True, verbose_name='描述')

    # 权限穿件时候显示job名称而不是ID
    def __str__(self):
        # return '%s object (%s)' % (self.__class__.__name__, self.pk)
        # return '{0.name}({0.pk})'.format(self)
        return self.name

    class Meta:
        verbose_name = _("JenkinsCi")
        unique_together = [('org_id', 'name')]
        ordering = ('name',)


class JenkinsNode(CommonModelMixin, OrgModelMixin):
    name = models.CharField(max_length=50, verbose_name='节点名')
    comment = models.TextField(blank=True, verbose_name='描述')

    class Meta:
        verbose_name = _("JenkinsNode")
        unique_together = [('org_id', 'name')]
        ordering = ('name',)
