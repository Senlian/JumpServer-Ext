#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xmltodict
import hashlib
import json

from django.db.transaction import atomic
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from jenkins import Jenkins, NotFoundException
from xml.dom.minidom import parseString

from orgs.utils import get_current_org_id, tmp_to_root_org, set_to_root_org, set_to_default_org, set_current_org
from cis.models import JenkinsCi
from cis.models import JenkinsNode

# from settings.models import Setting

JENKINS_URL = "http://192.168.159.10:9001/"
JENKINS_USERNAME = "gm"
JENKINS_PASSWORD = "123=abc"
__all__ = ["JenkinsApi", "JobList"]

# JENKINS_SETTINGS = {
#     'JENKINS_URL': "http://192.168.159.10:9001/",
#     'JENKINS_USERNAME': "gm",
#     'JENKINS_PASSWORD': "123=abc"
# }
UserModel = get_user_model()


class JobList(list):
    '''
        自定义list类，用以封装排序和搜索方法
    '''

    def __init__(self, seq=(), jks=None):
        self.jks = jks
        super(JobList, self).__init__(seq=seq)

    # 字段排序
    def order_by(self, *ordering):
        if len(ordering) < 1:
            return self
        lorder, sep, rorder = ordering[0].partition('-')
        order = rorder if sep else lorder
        self.sort(key=lambda x: x.get(order), reverse=(order != rorder))
        return self

    # 根据条件进行字段搜索
    def filter(self, *conditions):
        def is_filter(job):
            for condition in conditions:
                connector = condition.connector
                for fields, value in condition.children:
                    field, method = fields.split('__')
                    if method == 'eq':
                        if value.lower() == job.get(field, '').lower():
                            return True
                    else:
                        if value.lower() in job.get(field, '').lower():
                            return True
                    if connector != 'OR':
                        break
            return False

        super(JobList, self).__init__([job for job in self if is_filter(job)])
        return self

    def delete(self, job=None):
        jobs = [job] if job else self
        for job in jobs:
            if not isinstance(job, dict):
                continue
            job_name = job.get('name')
            if not job_name:
                continue
            job_db = self.jks.model.objects.filter(name=job_name)
            if self.jks.job_exists(name=job_name):
                self.jks.delete_job(name=job_name)
                self.jks.job_invalid(job_db)
            del job
        return self

    def issubset(self, obj):
        return all([(job in obj) for job in self])

    # 批量激活任务
    def enable_job(self, job=None):
        jobs = [job] if job else self
        for job in jobs:
            if not isinstance(job, dict):
                continue
            job_name = job.get('name')
            if not job_name:
                continue
            if self.jks.job_exists(name=job_name):
                self.jks.enable_job(name=job_name)
        return self

    # 批量禁用任务
    def disable_job(self, job=None):
        jobs = [job] if job else self
        for job in jobs:
            if not isinstance(job, dict):
                continue
            job_name = job.get('name')
            if not job_name:
                continue
            if self.jks.job_exists(name=job_name):
                self.jks.disable_job(name=job_name)
        return self


def get_jenkins_setting(item):
    cache_key = '_SETTING_' + item
    value = cache.get(cache_key)
    # value = Setting.objects.filter(name=item).first()
    # return getattr(settings, item, None) if not value else value.get(item)
    return getattr(settings, item, None) if not value else value



class JenkinsApi(Jenkins):
    model = JenkinsCi
    nodeDB = JenkinsNode

    def __init__(self, url=None, username=None, password=None, db=True):
        url = url or get_jenkins_setting('JENKINS_URL')
        username = username or get_jenkins_setting('JENKINS_USERNAME')
        password = password or get_jenkins_setting('JENKINS_PASSWORD')
        super(JenkinsApi, self).__init__(url=url, username=username, password=password)
        if db:
            self.initDB()

    def __call__(self, *args, **kwargs):
        return self.get_jenkins_jobs(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(exc_type)
            print(exc_val)
            print(exc_tb)
            return True
        return True

    def job_invalid(self, jobs):
        for job in jobs:
            if not self.job_exists(job.name):
                job.delete()

    def node_invalis(self, nodes):
        for node in nodes:
            if not self.node_exists(node.name):
                node.delete()

    @atomic
    def job_save_to_db(self, **kwargs):
        if not kwargs:
            return False
        try:
            return self.model.objects.create(**kwargs)
        except Exception as e:
            return False

    def initDB(self):
        new_jobs = []
        try:
            #  获取数据库中所有的job和node信息，判断是否是正确的，不正确则删除
            with tmp_to_root_org():
                jobs_in_db = self.model.objects.all()
                nodes_in_db = self.nodeDB.objects.all()
                self.job_invalid(jobs_in_db)
                self.node_invalis(nodes_in_db)
            # 现有job写入数据库
            # print('jobs=', json.dumps(self.get_jenkins_jobs(init=True)))
            for job in self.get_jenkins_jobs(init=True):
                job_data = {
                    'name': job.get('name'),
                    'org_id': '',
                    'created_by': UserModel._default_manager.get(role='Admin', name='Administrator')
                }
                new_job = self.job_save_to_db(**job_data)
                if new_job:
                    new_jobs.append(new_job)
            return all(new_jobs)
        except Exception as e:
            return False

    def get_jenkins_jobs(self, *args, **kwargs):
        jobs = JobList(jks=self)
        jobs_in_db = kwargs.get('jobs_in_db', [])
        init = kwargs.get('init', False)
        try:
            for i, job in enumerate(self.get_jobs()):
                jobName = job.get('name')
                if 'jobs' in job:
                    ijobs = job.get('jobs')
                    for ijob in ijobs:
                        ijobName = ijob['name'] = jobName + '/' + ijob.get('name')
                        jobinfo = self.get_job_info(ijobName)
                        ijob['status'] = jobinfo.get('color')
                        ijob['url'] = jobinfo.get('url')
                        ijob['label'] = jobinfo.get('labelExpression') or 'master'
                        ijob['fullname'] = jobinfo.get('fullName') or ijobName
                        ijob['nextBuildNumber'] = jobinfo.get('nextBuildNumber')
                        # DB过滤，初始化则不过滤DB
                        if not init:
                            if (not jobs_in_db) or (ijobName not in jobs_in_db):
                                continue
                        jobs.append(ijob)
                    continue
                if not init:
                    if (not jobs_in_db) or (jobName not in jobs_in_db):
                        continue
                jobinfo = self.get_job_info(jobName)
                job['status'] = jobinfo.get('color')
                job['url'] = jobinfo.get('url')
                job['label'] = jobinfo.get('labelExpression') or 'master'
                job['nextBuildNumber'] = jobinfo.get('nextBuildNumber')
                jobs.append(job)
        except Exception as e:
            raise (e)
        finally:
            return jobs

    # 执行groovy脚本
    def run_script(self, script=None, node=None):
        if not script:
            return []
        data = {'script': "{0}".format(script).encode('utf-8')}
        SCRIPT_TEXT = 'scriptText'
        NODE_SCRIPT_TEXT = 'computer/%(node)s/scriptText'
        if node:
            url = self._build_url(NODE_SCRIPT_TEXT, locals())
        else:
            url = self._build_url(SCRIPT_TEXT, locals())

        result = self.jenkins_open(requests.Request(
            'POST', url, data=data))

        return result[result.find(':') + 2:result.rfind('\n')].strip('[').strip(']').replace(' ', '').split(',')

    # 获取任务参数
    def get_job_parameters(self, jobName=None):
        if not jobName or not self.job_exists(jobName):
            raise NotFoundException('{0} is not a right jenkins job name !'.format(jobName))
        argvList = {}
        referencedDict = {}
        job_config = self.get_job_config(jobName)
        # 加载xml配置
        job_xml = parseString(job_config)
        # 获取参数根节点
        parameterDefinitions = job_xml.getElementsByTagName('parameterDefinitions')
        if not parameterDefinitions:
            return argvList, referencedDict
        # 获取参数子节点
        nodes = parameterDefinitions[0].childNodes
        for node in nodes:
            # 空行过滤
            if not node.toxml().strip():
                continue
            # json化参数配置
            nodeJson = xmltodict.parse(node.toxml(), encoding='utf-8')
            if not nodeJson:
                continue
            for key in nodeJson:
                argv = {}
                # 获取参数项
                parameter = nodeJson.get(key)
                # 参数名
                argName = argv['name'] = parameter.get('name')
                argv['key'] = key
                md5 = hashlib.md5()
                if not argName:
                    continue
                md5.update(argv.get('name').encode("utf-8"))
                prefix = key.split('.')[-1].split('Parameter')[0].lower() + '-parameter-'
                # 字段唯一ID
                argvId = argv['randomName'] = prefix + md5.hexdigest()
                argv['description'] = parameter.get('description')
                argv['defaultValue'] = ""
                argv['choiceType'] = "ET_TEXT_BOX"
                argv['choices'] = []
                argv['secureScript'] = ""
                argv['secureFallbackScript'] = ""
                argv['referencedParameters'] = []
                # Boolean 类型参数
                if key == 'hudson.model.BooleanParameterDefinition':
                    argv['defaultValue'] = False
                    argv['choiceType'] = "PT_SINGLE_SELECT"
                    argv['choices'] = [True, False]
                # Active choices parameters
                elif key in ['org.biouno.unochoice.ChoiceParameter', ]:
                    argv['randomName'] = parameter.get('randomName')
                    argv['choiceType'] = parameter.get('choiceType')
                    script = parameter.get('script')
                    if script:
                        argv['secureScript'] = script.get('secureScript', {}).get('script', '')
                        argv['secureFallbackScript'] = script.get('secureFallbackScript', {}).get('script', '')
                        try:
                            argv['choices'] = self.run_script(argv.get('secureScript'))
                        except:
                            argv['choices'] = self.run_script(argv.get('secureFallbackScript'))
                    argv['defaultValue'] = argv.get('defaultValue')
                # Choices parameters
                elif key == 'hudson.model.ChoiceParameterDefinition':
                    argv['choiceType'] = "PT_SINGLE_SELECT"
                    argv['choices'] = parameter.get('choices', {}).get('a', {}).get('string', [])
                elif key in ['hudson.model.PasswordParameterDefinition',
                             'hudson.model.StringParameterDefinition',
                             'hudson.model.TextParameterDefinition']:
                    trim = parameter.get('trim', False)
                    argv['defaultValue'] = parameter.get('defaultValue', '').strip() if trim else parameter.get(
                        'defaultValue')
                # # Active choices reacive parameters
                elif key in ['org.biouno.unochoice.DynamicReferenceParameter',
                             'org.biouno.unochoice.CascadeChoiceParameter']:
                    argv['choiceType'] = parameter.get('choiceType', 'PT_SINGLE_SELECT')
                    script = parameter.get('script')
                    referencedParameters = parameter.get('referencedParameters')
                    referencedParameters = [] if not referencedParameters else referencedParameters.split(',')
                    argv['referencedParameters'] = referencedParameters
                    preScript = ''
                    # 处理参数依赖,预先将依赖参数值写到脚本开头
                    for referencedParameter in referencedParameters:
                        referencedList = referencedDict.get(referencedParameter, [])
                        referencedList.append({'name': argName, 'id': argvId})
                        referencedDict[referencedParameter] = referencedList
                        preScript += 'def ' + referencedParameter + '="{' + referencedParameter + '}"\n'
                    if script:
                        secureScript = script.get('secureScript', {}).get('script', '')
                        secureFallbackScript = script.get('secureFallbackScript', {}).get('script', '')
                        if secureScript:
                            argv['secureScript'] = preScript + secureScript
                        if secureFallbackScript:
                            argv['secureFallbackScript'] = preScript + secureFallbackScript
                        doSecureScript = argv.get('secureScript')
                        doSecureFallbackScript = argv.get('secureFallbackScript')
                        referencedParameterChoices = [
                            referencedParameter.get('choices', [referencedParameter.get('defaultValue', '')])[0] \
                                if referencedParameter.get('choiceType') != 'PT_MULTI_SELECT' else \
                                [referencedParameter.get('choices', [referencedParameter.get('defaultValue', '')])[0]]
                            for referencedParameter in argvList.values() \
                            if referencedParameter.get('name') in referencedParameters]
                        format_dict = dict(zip(referencedParameters, referencedParameterChoices))
                        try:
                            argv['choices'] = self.run_script(doSecureScript.format(**format_dict))
                        except:
                            argv['choices'] = self.run_script(doSecureFallbackScript.format(**format_dict))

                # 单选下拉框
                if argv.get('choiceType') in ['PT_RADIO', 'PT_SINGLE_SELECT']:
                    argv['choiceType'] = 'PT_SINGLE_SELECT'
                # 多选下拉框
                elif argv.get('choiceType') in ['PT_MULTI_SELECT', 'PT_CHECKBOX']:
                    argv['choiceType'] = 'PT_MULTI_SELECT'
                # 文本框
                else:
                    argv['choiceType'] = 'ET_TEXT_BOX'
                argvList.update({argName: argv})
        return argvList, referencedDict


if __name__ == '__main__':
    api = JenkinsApi(JENKINS_URL, JENKINS_USERNAME, JENKINS_PASSWORD)

    #
    # # argvList, referencedDict = api.get_job_parameters('job7')
    # print(json.dumps(api.get_jobs(), indent=2))
    # print(json.dumps(api.get_job_info('dfdfd'), indent=2))
    print(json.dumps(api.get_jenkins_jobs('test'), indent=2))
    # print(json.dumps(api.get_job_info('dddd'), indent=2))
    # print(json.dumps(api.get_job_info('Job2')['nextBuildNumber'], indent=2))
    # print(json.dumps(api.get_build_console_output('Job2', 21), indent=2))
