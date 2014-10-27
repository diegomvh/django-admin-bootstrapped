#!/usr/bin/env python

def application(request):
    return {
        'application': request.application,
        'current_app': request.application.name
    }