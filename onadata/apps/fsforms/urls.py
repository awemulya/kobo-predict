from django.conf.urls import url
from .views import (
        LibraryFormsListView,
        assign, fill_details
        )


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assign/(?P<pk>[^/]+)$', assign, name="assign"),
        url(r'^fill-details/(?P<pk>[^/]+)$', fill_details, name="fill_details"),
]
