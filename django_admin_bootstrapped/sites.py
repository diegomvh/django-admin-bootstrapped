#!/usr/bin/env python
# encoding: utf-8

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.shortcuts import redirect
from django.views.decorators.cache import never_cache

from django.template.response import SimpleTemplateResponse
from django.utils.html import escape, escapejs

#from apps.account import auth
from .models import Application
from .options import ModelApplication
from .actions import delete_selected

TabularInline = admin.TabularInline
StackedInline = admin.StackedInline

class ApplicationSite(admin.AdminSite):
    base_site_template = "admin/base_site.html"
    def __init__(self, name):
        if Application.objects.db_table_exists():
            self.application, _ = Application.objects.get_or_create(name = name, defaults = {
                "title": name.title(),
                "description": "%s application" % name.title()
            })
        super(ApplicationSite, self).__init__(name)
        self.site_title = "%s Title" % self.name
        self.site_header = "%s Header" % self.name
        self._actions = {'delete_selected': delete_selected}
    
    def register(self, model_or_iterable, admin_class=None, **options):
        super(ApplicationSite, self).register(model_or_iterable, admin_class or ModelApplication, **options)
    
    # ------- From django 1.7
    def each_context(self):
        """
        Returns a dictionary of variables to put in the template context for
        *every* page in the admin site.
        """
        return {
            'site_title': self.site_title,
            'site_header': self.site_header,
            'base_site_template': self.base_site_template
        }
    
    def _has_permission(self, request):
        user = request.user
        organizacion = request.organizacion
        if user.is_active and (self.application.users.filter(pk = user.pk).exists() or user.is_superuser):
            
            # Veamos si esta bien la organizacion
            ancestors = organizacion.get_ancestors(include_self=True)
            if self.application.organizaciones.filter(pk__in=ancestors).exists():
                return True

            # Intentamos cambiar a una organizacion del usuario
            for org in user.organizaciones.all():
                ancestors = org.get_ancestors(include_self=True)
                if self.application.organizaciones.filter(pk__in=ancestors).exists():
                    user.set_roles_en_organizacion(org)
                    auth.set_user_organizacion(request, user, org)
                    return True

            # Intentamos cambiar a una organizacion de la aplicacion
            for org in self.application.organizaciones.all():
                ancestors = org.get_ancestors(include_self=True)
                if self.application.organizaciones.filter(pk__in=ancestors).exists():
                    user.set_roles_en_organizacion(org)
                    auth.set_user_organizacion(request, user, org)
                    return True

        return False

    @never_cache
    def login(self, request, extra_context = None):
        return redirect(settings.LOGIN_URL  + "?next=" + request.path)
        
    @never_cache
    def index(self, request, extra_context=None):
        context = dict(self.each_context())
        context.update(extra_context or {})
        return super(ApplicationSite, self).index(request, context)
    
    @never_cache
    def app_index(self, request, app_label, extra_context=None):
        context = dict(self.each_context())
        context.update(extra_context or {})
        return super(ApplicationSite, self).app_index(request, app_label, context)
    