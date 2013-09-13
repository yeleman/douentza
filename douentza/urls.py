from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    # Android API
    url(r'^fondasms/?$', 'douentza.views.fondasms.fondasms_handler',
        name='fondasms'),
    url(r'^fondasms/tester?$', 'douentza.views.fondasms.fondasms_tester',
        name='fondasms_tester'),

    # API
    url(r'^api/all_events/?$', 'douentza.views.event_dashboard.events_json',
        name='all_events_json'),
    url(r'^api/event_response_counts/?$', 'douentza.views.statistics.event_response_counts_json',
        name='event_response_counts'),
    url(r'^api/all_tags/?$', 'douentza.views.tags.all_tags',
        name='all_tags_json'),
    url(r'^api/tags/(?P<request_id>[0-9]+)/?$', 'douentza.views.tags.tags_for',
        name='tags_for_json'),
    url(r'^api/tags/(?P<request_id>[0-9]+)/update/?$', 'douentza.views.tags.update_tags',
        name='update_tags'),

    url(r'^entities/(?P<parent_slug>\d{8})/?$', 'douentza.views.events.entities_api', name='entities'),
    url(r'^statistics/$', 'douentza.views.statistics.dashboard', name='statistics'),
    url(r'^$', 'douentza.views.event_dashboard.dashboard', name='event_dashboard'),
    url(r'^change/(?P<event_id>[0-9]+)/(?P<new_status>[a-zA-Z\_]+)$',
        'douentza.views.event_dashboard.change_event_status', name='change_event'),
    url(r'^blacklist/(?P<blacknum_id>[0-9]+)?$', 'douentza.views.events.blacklist', name='blacklist'),
    url(r'^request/(?P<event_id>[0-9]+)/?$',
        'douentza.views.events.display_event', name='display_event'),
    url(r'^survey/(?P<survey_id>[0-9]+)-(?P<request_id>[0-9]+)/form/?$', 'douentza.views.surveys.survey_form', name='mini_survey_form'),
    url(r'^survey/(?P<survey_id>[0-9]+)-(?P<request_id>[0-9]+)/data/?$', 'douentza.views.surveys.survey_data', name='mini_survey_data'),
    url(r'^survey/(?P<survey_id>[0-9]+)-(?P<request_id>[0-9]+)/exists/?$', 'douentza.views.surveys.survey_exists', name='mini_survey_exists'),
)
