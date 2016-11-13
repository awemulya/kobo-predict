from django.conf.urls import url
from .views import assign



urlpatterns = [
        url(r'^assign/(?P<id_string>[^/]+)$', assign, name="assign"),
]
