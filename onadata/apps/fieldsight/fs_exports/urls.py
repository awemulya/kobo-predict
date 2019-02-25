from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^xls/project/site/list/(?P<pk>[0-9]+)/$', views.ExportProjectSitesWithRefs.as_view(), name='export_xls_project_level_sites'),
    url(r'^xls/project/(?P<pk>[0-9]+)/region/(?P<region_id>[0-9]+)/site/list/$', views.ExportProjectSitesWithRefs.as_view(), name='export_xls_region_sites'),
    url(r'^clone/project/from/(?P<pk>[0-9]+)/to/(?P<t_pk>[0-9]+)/$', views.CloneProjectSites.as_view(), name='clone_project_sites'),
    url(r'^xls/project/site/list/metas/(?P<pk>\d+)/$', views.ExportProjectSitesWithRefs.as_view(), name="export_xls_region_sites_post"),
    url(r'^xls/project/$', views.ExportOptions.as_view(), name="exportOptions"),
    url(r'^xls/project/responses/(?P<pk>[0-9]+)/$', views.ExportProjectFormsForSites.as_view(), name='export_xls_project_sites'),
    url(r'^zip/site-images/(?P<pk>[0-9]+)/(?P<size_code>[0-9]+)/$', views.ImageZipSites.as_view(), name='image_zip_sites'),
    url(r'^project/statstics/(?P<pk>[0-9]+)/$', views.ProjectStatsticsReport.as_view(), name='project_stats_report'),
    url(r'^logs/(?P<pk>[0-9]+)/$', views.LogsReport.as_view(), name='logs_report'),
    url(r'^xls/project/stages_status_report/(?P<pk>\d+)/$', views.StageStatus.as_view(), name='download-stages'),
    ]