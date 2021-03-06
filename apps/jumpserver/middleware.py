# ~*~ coding: utf-8 ~*~

import os
import re
import pytz
from django.utils import timezone
from django.shortcuts import HttpResponse
from django.conf import settings

from .utils import set_current_request


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = request.META.get('TZ')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        response = self.get_response(request)
        return response


class DemoMiddleware:
    # demo演示
    DEMO_MODE_ENABLED = os.environ.get("DEMO_MODE", "") in ("1", "ok", "True")
    # demo演示地址
    SAFE_URL_PATTERN = re.compile(
        r'^/users/login|'
        r'^/api/terminal/v1/.*|'
        r'^/api/terminal/.*|'
        r'^/api/users/v1/auth/|'
        r'^/api/users/v1/profile/'
    )
    SAFE_METHOD = ("GET", "HEAD")

    def __init__(self, get_response):
        self.get_response = get_response

        if self.DEMO_MODE_ENABLED:
            print("Demo mode enabled, reject unsafe method and url")

    def __call__(self, request):
        if self.DEMO_MODE_ENABLED and request.method not in self.SAFE_METHOD \
                and not self.SAFE_URL_PATTERN.match(request.path):
            return HttpResponse("Demo mode, only safe request accepted", status=403)
        else:
            response = self.get_response(request)
            return response


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        is_request_api = request.path.startswith('/api')
        if not settings.SESSION_EXPIRE_AT_BROWSER_CLOSE and not is_request_api:
            age = request.session.get_expiry_age()
            # 添加_session_expiry字段
            request.session.set_expiry(age)
        return response
