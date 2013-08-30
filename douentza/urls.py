from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^stats/$', 'douentza.views.stats', name='stats'),
    # url(r'^graph_url/$', 'douentza.views.graph_data_json', name='graph_url'),

    url(r'^test$', 'douentza.views.form_test.tester', name='tester'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

    url(r'^$', 'douentza.views.event_dashboard.dashboard', name='event_dashboard'),

    # API
    url(r'^api/all_events/?$', 'douentza.views.event_dashboard.events_json', name='all_events_json'),

)
