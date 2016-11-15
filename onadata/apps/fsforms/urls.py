from django.conf.urls import url
from .views import (
        LibraryFormsListView,
        assign
        )



urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assign/(?P<id_string>[^/]+)$', assign, name="assign"),
]
