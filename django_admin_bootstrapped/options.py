#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib.admin.templatetags.admin_static import static
from django.contrib.admin.options import csrf_protect_m
from django import forms
from django.shortcuts import redirect
from django.db import transaction
from django.views.decorators.cache import never_cache
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_text

from django.template.response import SimpleTemplateResponse
from django.utils.html import escape, escapejs

from .models import Application

IS_POPUP_VAR = '_popup'

import logging

logger = logging.getLogger(__name__)

class TabularInline(admin.TabularInline):
    pass

class StackedInline(admin.StackedInline):
    pass

def modelApplicationFactory(BaseModelAdmin):
    class ModelApplication(BaseModelAdmin):
        default_filters = None

        @csrf_protect_m
        @transaction.atomic
        def add_view(self, request, form_url='', extra_context=None):
            context = dict(self.admin_site.each_context())
            context.update(extra_context or {})
            return super(ModelApplication, self).add_view(request, form_url, context)

        @csrf_protect_m
        @transaction.atomic
        def change_view(self, request, object_id, form_url='', extra_context=None):
            context = dict(self.admin_site.each_context())
            context.update(extra_context or {})
            return super(ModelApplication, self).change_view(request, object_id, form_url, context)

        @csrf_protect_m
        def changelist_view(self, request, extra_context=None):
            if self.default_filters:
                try:
                    test = request.META['HTTP_REFERER'].split(request.META['PATH_INFO'])
                    if test and test[-1] and not test[-1].startswith('?'):
                        url = reverse('%s:%s_%s_changelist' % (self.admin_site.name, self.opts.app_label, self.opts.module_name))
                        filters = []
                        for filter in self.default_filters:
                            key = filter.split('=')[0]
                            if not request.GET.has_key(key):
                                filters.append(filter)
                        if filters:                        
                            return HttpResponseRedirect("%s?%s" % (url, "&".join(filters)))
                except: 
                    pass
            context = dict(self.admin_site.each_context())
            context.update(extra_context or {})
            return super(ModelApplication, self).changelist_view(request, context)

        @csrf_protect_m
        @transaction.atomic
        def delete_view(self, request, object_id, extra_context=None):
            context = dict(self.admin_site.each_context())
            context.update(extra_context or {})
            return super(ModelApplication, self).delete_view(request, object_id, context)

        def history_view(self, request, object_id, extra_context=None):
            context = dict(self.admin_site.each_context())
            context.update(extra_context or {})
            return super(ModelApplication, self).history_view(request, object_id, context)
            
        # Vamos a permitir los changes con popup en nuestro site
        def response_change(self, request, obj):
            if IS_POPUP_VAR in request.POST:
                return SimpleTemplateResponse('applications/popup_response.html', {
                    'pk_value': escape(obj._get_pk_val()),
                    'obj': escapejs(obj)
                })
            else:
                return super(ModelApplication, self).response_change(request, obj)
    
        def log_addition(self, request, object):
            """
            Log that an object has been successfully added.
    
            The default implementation creates an admin LogEntry object.
            """
            from django.contrib.admin.models import LogEntry, ADDITION
            logger.error('There was some crazy error', exc_info=True, extra={
                # Optionally pass a request and we'll grab any information we can
                'request': request,
                'user_id':request.user.pk,
                'content_type_id':ContentType.objects.get_for_model(object).pk,
                'object_id':object.pk,
                'object_repr':force_text(object),
                'action_flag':ADDITION
            })
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(object).pk,
                object_id=object.pk,
                object_repr=force_text(object),
                action_flag=ADDITION
            )
    
        def log_change(self, request, object, message):
            """
            Log that an object has been successfully changed.
    
            The default implementation creates an admin LogEntry object.
            """
            from django.contrib.admin.models import LogEntry, CHANGE
            print LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(object).pk,
                object_id=object.pk,
                object_repr=force_text(object),
                action_flag=CHANGE,
                change_message=message
            )
    
        def log_deletion(self, request, object, object_repr):
            """
            Log that an object will be deleted. Note that this method is called
            before the deletion.
    
            The default implementation creates an admin LogEntry object.
            """
            from django.contrib.admin.models import LogEntry, DELETION
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(self.model).pk,
                object_id=object.pk,
                object_repr=object_repr,
                action_flag=DELETION
            )
    return ModelApplication
    
ModelApplication = modelApplicationFactory(admin.ModelAdmin)