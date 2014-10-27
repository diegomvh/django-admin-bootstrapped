#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from django.utils.functional import SimpleLazyObject
from apps.application.models import get_current_application

def get_application(request):
    if not hasattr(request, '_cached_application'):
        request._cached_application = get_current_application(request)
    return request._cached_application

class ApplicationMiddleware(object):
    def process_request(self, request):
        assert hasattr(request, 'session'), "The Django authentication middleware requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."
        request.application = SimpleLazyObject(lambda: get_application(request))
