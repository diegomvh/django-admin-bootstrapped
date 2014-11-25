from __future__ import unicode_literals

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models.signals import pre_save, pre_delete
from django.db import connection

from mptt import models as mpttmodels
from apps.account import models as account
from apps.core import models as coremodels

APPLICATION_CACHE = {}

def get_request_application_name(request):
    from django.conf import settings
    path = request.path
    if settings.FORCE_SCRIPT_NAME and path.startswith(settings.FORCE_SCRIPT_NAME):
        path = path[len(settings.FORCE_SCRIPT_NAME):]
    return path.split("/")[1]

class ApplicationManager(models.Manager):

    def db_table_exists(self):
        return self.model()._meta.db_table in connection.introspection.table_names()
    
    def clear_cache(self):
        """Clears the ``Application`` object cache."""
        global APPLICATION_CACHE
        APPLICATION_CACHE = {}

class Application(models.Model):
    name = models.SlugField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    users = models.ManyToManyField(account.RoleUser)
    organizaciones = mpttmodels.TreeManyToManyField(coremodels.Organizacion)
    objects = ApplicationManager()
    
    def __str__(self):
        return self.name.title()
        
    def get_index_url(self):
        return "%s:index" % self.name
        
class RequestSite(object):
    def __init__(self, request):
        self.name = get_request_application_name(request)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False):
        raise NotImplementedError('RequestSite cannot be saved.')

    def delete(self):
        raise NotImplementedError('RequestSite cannot be deleted.')

def get_current_application(request):
    current_application = RequestSite(request)
    if Application._meta.installed:
        application_name = get_request_application_name(request)
        try:
            current_application = APPLICATION_CACHE[application_name]
        except KeyError:
            apps = Application.objects.filter(name=application_name)
            if apps.exists():
                APPLICATION_CACHE[application_name] = current_application = apps.first()
    return current_application

def clear_application_cache(sender, **kwargs):
    """Clears the cache (if primed) each time a site is saved or deleted"""
    instance = kwargs['instance']
    try:
        del APPLICATION_CACHE[instance.pk]
    except KeyError:
        pass
pre_save.connect(clear_application_cache, sender=Application)
pre_delete.connect(clear_application_cache, sender=Application)
