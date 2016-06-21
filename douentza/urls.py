#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.contrib.auth import views as auth_views

from fondasms import views as fonda_views

from douentza import views as views

admin.autodiscover()

SURVEY_ID = r'(?P<survey_id>[0-9]+)'
REQUEST_ID = r'(?P<request_id>[0-9]+)'

urlpatterns = [
    url(r'^download/(?P<fname>.*)$',
        views.cached_data.serve_cached_file, name='cached_file'),
    url(r'^exports/(?P<slug>[a-z0-9A-Z\-\_]+)$',
        views.cached_data.cached_data_lookup, name='cached_slug'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', auth_views.login,
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout,
        {'next_page': '/'}, name='logout'),

    # # Android API
    url(r'^fondasms/?$', fonda_views.fondasms_handler,
        {'handler_module': 'douentza.fondasms_handlers',
         'send_automatic_reply': True,
         'automatic_reply_via_handler': False,
         'automatic_reply_text': ("Thank You, we recorded your request."
                                  "You'll be called back shortly.")},
        name='fondasms'),

    # API
    url(r'^api/events/?$', views.api.events_api, name='events_api'),

    url(r'^api/event_response_counts/?$',
        views.statistics.event_response_counts_json,
        name='event_response_counts'),
    url(r'^api/all_tags/?$',
        views.tags.all_tags,
        name='all_tags_json'),
    url(r'^api/tags/' + REQUEST_ID + '/?$', views.tags.tags_for,
        name='tags_for_json'),
    url(r'^api/tags/' + REQUEST_ID + '/update/?$',
        views.tags.update_tags,
        name='update_tags'),
    url(r'^api/ping_json$', views.dashboard.ping_json,
        name='ping_json'),
    url(r'^api/ping_html$', views.dashboard.ping_html,
        name='ping_html'),

    url(r'^entities/(?P<parent_slug>[a-z0-9_\-]+)/?$',
        views.events.entities_api, name='entities'),
    url(r'^statistics/$', views.statistics.dashboard,
        name='statistics'),
    url(r'^survey_stats/$', views.surveys_stats.stats_for_surveys,
        name='stats_for_surveys'),
    url(r'^survey_stats/' + SURVEY_ID + r'/?$',
        views.surveys_stats.stats_for_survey,
        name='stats_for_survey'),
    url(r'^archives/?$', views.archives.archives, name='archives'),

    # admin
    url(r'^admin/surveys/?$', views.admin.admin_surveys,
        name='admin_surveys'),
    url(r'^admin/projects/?$', views.admin.admin_projects,
        name='admin_projects'),
    url(r'^admin/surveys/' + SURVEY_ID + '/?$',
        views.admin.admin_survey, name='admin_survey'),
    url(r'^admin/surveys/' + SURVEY_ID + '/delete-question/'
        r'(?P<question_id>[0-9]+)/?$',
        views.admin.admin_delete_question,
        name='admin_survey_delete_question'),
    url(r'^admin/surveys/' + SURVEY_ID + '/validate/?$',
        views.admin.admin_survey_validate,
        name='admin_survey_validate'),
    url(r'^admin/surveys/' + SURVEY_ID + '/toggle/?$',
        views.admin.admin_survey_toggle,
        name='admin_survey_toggle'),

    url(r'^$', views.dashboard.dashboard, name='dashboard'),
    url(r'^monitoring', views.monitoring.summary,
        name='monitoring'),
    url(r'^change/' + REQUEST_ID + r'/(?P<new_status>[a-zA-Z\_]+)$',
        views.dashboard.change_event_status, name='change_event'),
    url(r'^blacklist/(?P<blacknum_id>[0-9]+)?$',
        views.admin.admin_blacklist, name='blacklist'),

    url(r'^sorted_location/' + REQUEST_ID + r'/(?P<cluster_slug>[a-zA-Z\_]+)$',
        views.dashboard.sorted_location, name='sorted_location'),

    url(r'^request/' + REQUEST_ID + '/?$',
        views.events.display_request, name='display_request'),
    url(r'^archived_request/' + REQUEST_ID + '/?$',
        views.archives.archived_request, name='archived_request'),
    url(r'^survey/' + SURVEY_ID + '-' + REQUEST_ID + '/form/?$',
        views.surveys.survey_form, name='mini_survey_form'),
    url(r'^survey/' + SURVEY_ID + '-' + REQUEST_ID + '/data/?$',
        views.surveys.survey_data, name='mini_survey_data'),
]

# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += staticfiles_urlpatterns()
