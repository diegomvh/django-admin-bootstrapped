from django.conf.urls import patterns, include, url
from test_django_admin_bootstrapped.admin import site
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_django_admin_bootstrapped_p3.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(site.urls)),
)
