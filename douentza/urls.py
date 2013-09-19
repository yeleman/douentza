from django.conf.urls import patterns, include, url

from django.contrib import admin

admin.autodiscover()

SURVEY_ID = r'(?P<survey_id>[0-9]+)'
REQUEST_ID = r'(?P<request_id>[0-9]+)'

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
    url(r'^api/event_response_counts/?$', 'douentza.views.statistics.event_response_counts_json',
        name='event_response_counts'),
    url(r'^api/all_tags/?$', 'douentza.views.tags.all_tags',
        name='all_tags_json'),
    url(r'^api/tags/'+ REQUEST_ID +'/?$', 'douentza.views.tags.tags_for',
        name='tags_for_json'),
    url(r'^api/tags/'+ REQUEST_ID +'/update/?$', 'douentza.views.tags.update_tags',
        name='update_tags'),
    url(r'^api/ping_json$', 'douentza.views.event_dashboard.ping_json', name='ping_json'),

    url(r'^entities/(?P<parent_slug>\d{8})/?$', 'douentza.views.events.entities_api', name='entities'),
    url(r'^statistics/$', 'douentza.views.statistics.dashboard', name='statistics'),
    url(r'^survey_stats/$', 'douentza.views.surveys.survey_stats', name='survey_stats'),
    url(r'^archives/?$', 'douentza.views.events.archives', name='archives'),

    # export
    url(r'^export_general_stats_as_csv/?$', 'douentza.views.statistics.export_general_stats_as_csv',
        name='export_general_stats_as_csv'),

    # admin
    url(r'^admin/surveys/?$', 'douentza.views.admin.admin_surveys', name='admin_surveys'),
    url(r'^admin/projects/?$', 'douentza.views.admin.admin_projects', name='admin_projects'),
    url(r'^admin/surveys/'+ SURVEY_ID +'/?$', 'douentza.views.admin.admin_survey', name='admin_survey'),
    url(r'^admin/surveys/'+ SURVEY_ID +'/delete-question/(?P<question_id>[0-9]+)/?$',
        'douentza.views.admin.admin_delete_question', name='admin_survey_delete_question'),
    url(r'^admin/surveys/'+ SURVEY_ID +'/validate/?$', 'douentza.views.admin.admin_survey_validate',
        name='admin_survey_validate'),
    url(r'^admin/surveys/'+ SURVEY_ID +'/toggle/?$', 'douentza.views.admin.admin_survey_toggle',
        name='admin_survey_toggle'),

    url(r'^$', 'douentza.views.event_dashboard.dashboard', name='event_dashboard'),
    url(r'^change/'+ REQUEST_ID + '/(?P<new_status>[a-zA-Z\_]+)$',
        'douentza.views.event_dashboard.change_event_status', name='change_event'),
    url(r'^blacklist/(?P<blacknum_id>[0-9]+)?$', 'douentza.views.events.blacklist', name='blacklist'),
    url(r'^request/'+ REQUEST_ID +'/?$',
        'douentza.views.events.display_event', name='display_event'),
    url(r'^survey/'+ SURVEY_ID +'-'+ REQUEST_ID +'/form/?$', 'douentza.views.surveys.survey_form', name='mini_survey_form'),
    url(r'^survey/'+ SURVEY_ID +'-'+ REQUEST_ID +'/data/?$', 'douentza.views.surveys.survey_data', name='mini_survey_data'),
)
