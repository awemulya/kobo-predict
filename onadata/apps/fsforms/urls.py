from django.conf.urls import url
from .views import (
        LibraryFormsListView,
        FormsListView,
        StageListView,
        StageUpdateView,
        StageCreateView,
        ScheduleListView,
        ScheduleCreateView,
        ScheduleUpdateView,
        assign, fill_form_type,
        fill_details_stage,
        fill_details_schedule
        )


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned/$', FormsListView.as_view(), name='forms-list'),

        url(r'^stage/$', StageListView.as_view(), name='stage-list'),
        url(r'^stage/add/$', StageCreateView.as_view(), name='stage-add'),
        url(r'^stage/(?P<pk>[0-9]+)/$', StageUpdateView.as_view(), name='stage-edit'),
        url(r'^schedule/$', ScheduleListView.as_view(), name='schedule-list'),
        url(r'^schedule/add/$', ScheduleCreateView.as_view(), name='schedule-add'),
        url(r'^schedule/(?P<pk>[0-9]+)/$', ScheduleUpdateView.as_view(), name='schedule-edit'),

        url(r'^assign/(?P<pk>[0-9]+)/$', assign, name="assign"),
        url(r'^fill-form-type/(?P<pk>[0-9]+)/$', fill_form_type, name="fill_form_type"),
        url(r'^fill-details-stage/(?P<pk>[0-9]+)/$', fill_details_stage, name="fill_details_stage"),
        url(r'^fill-details-schedule/(?P<pk>[0-9]+)/$', fill_details_schedule, name="fill_details_schedule"),
]
