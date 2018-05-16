from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^xls/project/site/list/(?P<pk>[0-9]+)/$', views.ExportProjectSites.as_view(), name='export_xls_project_sites'),
]