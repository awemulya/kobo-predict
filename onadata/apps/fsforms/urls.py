from django.conf.urls import url
from .views import (
        LibraryFormsListView,
        FormsListView,
        assign, fill_form_type
        )


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned', FormsListView.as_view(), name='forms-list'),
        url(r'^assign/(?P<pk>[^/]+)$', assign, name="assign"),
        url(r'^fill-form-type/(?P<pk>[^/]+)$', fill_form_type, name="fill_form_type"),
]
