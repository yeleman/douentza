from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

from settings import MEDIA_ROOT

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'douentza.views.home', name='home'),
    # url(r'^douentza/', include('douentza.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^test$', 'douentza.views.form_test.tester', name='tester'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    url(r'^media/(?P<path>.*)$',
         'django.views.static.serve',
         {'document_root': MEDIA_ROOT, 'show_indexes': True},
         name='media'),
)
