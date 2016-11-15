from django.conf.urls import url
from .views import (
        LibraryFormsListView,
        FormsListView,
        assign, fill_form_type,
        fill_details_stage,
        fill_details_schedule
        )


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned', FormsListView.as_view(), name='forms-list'),
        url(r'^assign/(?P<pk>[0-9]+)/$', assign, name="assign"),
        url(r'^fill-form-type/(?P<pk>[0-9]+)/$', fill_form_type, name="fill_form_type"),
        url(r'^fill-details-stage/(?P<pk>[0-9]+)/$', fill_details_stage, name="fill_details_stage"),
        url(r'^fill-details-schedule/(?P<pk>[0-9]+)/$', fill_details_schedule, name="fill_details_schedule"),
]
