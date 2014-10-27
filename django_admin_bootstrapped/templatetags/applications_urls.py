from django.core.urlresolvers import reverse
from django import template
from django.contrib.admin.util import quote

register = template.Library()

@register.filter
def applications_urldelete(model, app):
	return '%s:%s_%s_%s' % (app, model._meta.app_label, model._meta.module_name, 'delete')

@register.filter
def applications_urlchange(model, app):
    return '%s:%s_%s_%s' % (app, model._meta.app_label, model._meta.module_name, 'change')

@register.filter
def applications_urlquote(value):
    return quote(value)
