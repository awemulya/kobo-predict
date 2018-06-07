from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^xls/project/site/list/(?P<pk>[0-9]+)/$', views.ExportProjectSites.as_view(), name='export_xls_project_sites'),
    url(r'^xls/project/(?P<pk>[0-9]+)/region/(?P<region_id>[0-9]+)/site/list/$', views.ExportProjectSites.as_view(), name='export_xls_region_sites'),
    url(r'^clone/project/from/(?P<pk>[0-9]+)/to/(?P<t_pk>[0-9]+)/$', views.CloneProjectSites.as_view(), name='clone_project_sites'),
    url(r'^xls/project/site/list/metas/(?P<pk>\d+)/$', views.ExportProjectSitesWithRefs.as_view(), name="test"),
    url(r'^xls/project/$', views.ExportOptions.as_view(), name="exportOptions"),
    ]