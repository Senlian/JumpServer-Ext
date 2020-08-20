"""
WSGI config for jumpserver project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jumpserver.settings")

# 此处调用WSGIHandler实例的call方法
application = get_wsgi_application()
