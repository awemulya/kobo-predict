from django.conf.urls import url
from . import views
from django.views.decorators.csrf import csrf_exempt
from fcm.views import DeviceViewSet
from onadata.apps.fieldsight.viewsets.FieldsightFcmViewset import FcmDeviceViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import OrganizationsProjectViewSet

from onadata.apps.fieldsight.viewsets.OrganizationViewset import OrganizationTypeViewSet, OrganizationViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import ProjectTypeViewSet, ProjectCreationViewSet, ProjectRegionslistViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import OrganizationsProjectViewSet
from onadata.apps.fieldsight.viewsets.RegionViewSet import RegionViewSet
from onadata.apps.fieldsight.viewsets.SiteViewSet import SiteViewSet, AllSiteViewSet, SiteCreationSurveyViewSet, \
    SiteReviewViewSet, ProjectTypeViewset, SiteReviewUpdateViewSet, SiteUnderProjectViewSet, SiteUpdateViewSet, \
    ProjectUpdateViewSet, SiteUnderOrgViewSet, SiteUnderRegionViewSet
from .forms import RegistrationForm

from .views import (
    OrganizationSearchView,
    ProjectSearchView,
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDeleteView,
    Organization_dashboard,
    alter_org_status,
    OrganizationadminCreateView,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    Project_dashboard,
    alter_proj_status,
    add_proj_manager,
    SiteListView,
    SiteCreateView,
    SiteUpdateView,
    SiteDeleteView,
    SiteDashboardView,
    alter_site_status,
    add_supervisor,
    CreateUserView,
    viewfullmap,
    OrgFullmap,
    ProjFullmap,
    SiteFullmap,
    OrganizationdataSubmissionView,
    ProjectdataSubmissionView,
    SitedataSubmissionView,
    RegionCreateView,
    RegionUpdateView,
    RegionDeleteView,
    RegionListView,
    UserListView, site_images, FilterUserView, UploadSitesView, BluePrintsView, add_project_role, ManagePeopleSiteView,
    ManagePeopleProjectView, ManagePeopleOrganizationView, SiteSurveyListView, ajax_upload_sites, ajax_save_site,
    ajax_save_project, RolesView, OrgProjectList, OrgUserList, ProjUserList, SiteUserList, ProjSiteList, OrgSiteList,
    senduserinvite, ActivateRole, checkemailforinvite, ProjectSummaryReport, SiteSummaryReport, MultiUserAssignSiteView, MultiUserAssignProjectView,
    stages_status_download, sendmultiroleuserinvite, project_html_export, RegionalSitelist, RegionalSiteCreateView )


urlpatterns = [
    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),

    url(r'^organization/$', OrganizationListView.as_view(), name='organizations-list'),
    url(r'^organization/$', OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/add/$', OrganizationCreateView.as_view(), name='organization-add'),
    url(r'^organization/(?P<pk>[0-9]+)/$', OrganizationUpdateView.as_view(), name='organization-edit'),
    url(r'^organization-dashboard/(?P<pk>[0-9]+)/$', Organization_dashboard.as_view(), name='organizations-dashboard'),
    url(r'^organization/delete/(?P<pk>\d+)/$', OrganizationDeleteView.as_view(), name='organization-delete'),
    url(r'^organization/alter-status/(?P<pk>\d+)/$', alter_org_status, name='alter_org_status'),
    url(r'^organization/add-org-admin/(?P<pk>\d+)/$', OrganizationadminCreateView.as_view(), name='add_org_admin'),

    url(r'^api/projects/(?P<pk>\d+)/$', ProjectCreationViewSet.as_view({'get': 'list'}), name='projects-list'),
    url(r'^api/projects/$', ProjectCreationViewSet.as_view({'post': 'create', 'put': 'update'}), name='projects-list'),
    url(r'^project/$', ProjectListView.as_view(), name='projects-list'),
    url(r'^project/$', ProjectListView.as_view(), name='project-list'),
    # url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/add/(?P<pk>[0-9]+)/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^project-dashboard/(?P<pk>[0-9]+)/$', Project_dashboard.as_view(), name='project-dashboard'),
    url(r'^api/org-projects/(?P<pk>\d+)/$', OrganizationsProjectViewSet.as_view({'get': 'list'})),
    url(r'^api/async_save_project/$', ajax_save_project),

    url(r'^org-projects/(?P<pk>\d+)/$', OrgProjectList.as_view(), name='org-project-list'),
    url(r'^org-users/(?P<pk>\d+)/$', OrgUserList.as_view(), name='org-user-list'),
    url(r'^org-sites/(?P<pk>\d+)/$', OrgSiteList.as_view(), name='org-site-list'),

    url(r'^proj-users/(?P<pk>\d+)/$', ProjUserList.as_view(), name='proj-user-list'),
    url(r'^proj-sites/(?P<pk>\d+)/$', ProjSiteList.as_view(), name='proj-site-list'),
    
    url(r'^site-users/(?P<pk>\d+)/$', SiteUserList.as_view(), name='site-user-list'),


    url(r'^upload/(?P<pk>\d+)/$', UploadSitesView.as_view(), name='site-upload'),
    url(r'^api/bulk_upload_site/(?P<pk>\d+)/$', ajax_upload_sites),
    url(r'^api/async_save_site/$', csrf_exempt(ajax_save_site)),
    url(r'^project/delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),
    url(r'^project/alter-status/(?P<pk>\d+)/$', alter_proj_status, name='alter_proj_status'),
    url(r'^project/stages_status_report/(?P<pk>\d+)/$', stages_status_download, name='download-stages'),
    url(r'^project/add-proj-manager/(?P<pk>\d+)/$', add_proj_manager, name='add_proj_manager'),
    url(r'^project/add-role/(?P<pk>\d+)/$', add_project_role, name='add_project_staffs'),
    url(r'^api/project-sites/(?P<pk>\d+)/$', SiteViewSet.as_view({'get': 'list'}), name='project_sites'),
    url(r'^api/update-site/(?P<pk>\d+)$', SiteUpdateViewSet.as_view({'post': 'update'}), name='update_site_api'),
    url(r'^api/update-project/(?P<pk>\d+)$', ProjectUpdateViewSet.as_view({'put': 'update'}), name='update_project_api'),


    url(r'^survey-sites/(?P<pk>\d+)$', SiteSurveyListView.as_view(), name='site-survey-list'),
    url(r'^api/sites/$', AllSiteViewSet.as_view({'get': 'list'}), name='sites-list'),
    url(r'^api/project-types/$', ProjectTypeViewset.as_view({'get': 'list'})),
    url(r'^api/survey-sites/(?P<pk>\d+)/$', SiteCreationSurveyViewSet.as_view({'get': 'list'}), name='sites-list'),
    url(r'^api/survey-sites-review/(?P<pk>\d+)/$', SiteReviewViewSet.as_view({'get': 'list'}), name='sites-list-review'),
    url(r'^api/project-sites/(?P<pk>\d+)/$', SiteUnderProjectViewSet.as_view({'get': 'list'}), name='project-sites-list'),
    url(r'^api/org-sites/(?P<pk>\d+)/$', SiteUnderOrgViewSet.as_view({'get': 'list'}), name='org-sites-list'),
    url(r'^api/survey-sites-review-update/(?P<pk>\d+)/$', SiteReviewUpdateViewSet.as_view({'post': 'update'})),
    url(r'^api/survey-sites/$', SiteCreationSurveyViewSet.as_view({'post': 'create', 'put':'update'}), name='sites-list'),
    url(r'^site/$', SiteListView.as_view(), name='sites-list'),
    url(r'^site/$', SiteListView.as_view(), name='site-list'),
    url(r'^site/add/(?P<pk>[0-9]+)/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^site/(?P<pk>[0-9]+)/$', SiteUpdateView.as_view(), name='site-edit'),

    url(r'^site/blue-prints/(?P<id>[0-9]+)/$', BluePrintsView.as_view(), name='site-blue-prints'),

    url(r'^site-dashboard/(?P<pk>[0-9]+)/$', SiteDashboardView.as_view(), name='site-dashboard'),

    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),
    url(r'^site/alter-status/(?P<pk>\d+)/$', alter_site_status, name='alter_site_status'),
    url(r'^site/add-supervisor/(?P<pk>\d+)/$', add_supervisor, name='add_supervisor'),
    url(r'^api/site-images/(?P<pk>\d+)/$', site_images, name='site_images'),

    url(r'^manage/people/site/(?P<pk>\d+)/$', ManagePeopleSiteView.as_view(), name='manage-people-site'),
    url(r'^manage/people/project/(?P<pk>\d+)/$', ManagePeopleProjectView.as_view(), name='manage-people-project'),
    url(r'^manage/people/organization/(?P<pk>\d+)/$', ManagePeopleOrganizationView.as_view(), name='manage-people-organization'),

    url(r'^multi-user-assign-site/(?P<pk>\d+)/$', MultiUserAssignSiteView.as_view(), name='multi_user_site_assign'),
    url(r'^multi-user-assign-project/(?P<pk>\d+)/$', MultiUserAssignProjectView.as_view(), name='multi_user_project_assign'),

    url(r'^accounts/create/$', CreateUserView.as_view(form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
    url(r'^filter-users/$', FilterUserView.as_view(), name='filter-users'),
    url(r'fcm/v1/devices/$', DeviceViewSet.as_view({'get': 'list'})),
    url(r'fcm/add/', FcmDeviceViewSet.as_view({'post': 'create'})),
    url(r'fcm/logout/', FcmDeviceViewSet.as_view({'post': 'inactivate'})),
    url(r'myroles/', RolesView.as_view(), name='roles-dashboard'),
    url(r'^senduserinvite/$', senduserinvite, name='senduserinvite'),
    url(r'^sendmultiusermultilevelinvite/$', sendmultiroleuserinvite, name='sendmultiroleuserinvite'),
    url(r'^checkemailforinvite/$', checkemailforinvite, name='check-email-for-invite'),
    url(r'^activaterole/(?P<invite_idb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$',
        ActivateRole.as_view(), name='activate-role'),
    url(r'^project/report/summary/(?P<pk>\d+)/$', ProjectSummaryReport.as_view(), name='project-summary-report'),
    url(r'^site/report/summary/(?P<pk>\d+)/$', SiteSummaryReport.as_view(), name='site-summary-report'),
    url(r'map-view/$',views.viewfullmap, name='full-map'),
    url(r'org-map/(?P<pk>[0-9]+)/$', OrgFullmap.as_view(), name='org-loc-map'),
    url(r'proj-map/(?P<pk>[0-9]+)/$', ProjFullmap.as_view(), name='proj-loc-map'),
    url(r'site-map/(?P<pk>[0-9]+)/$', SiteFullmap.as_view(), name='site-loc-map'),
    url(r'^org-submission/(?P<pk>[0-9]+)/(?P<type>[0-9]+)/$', OrganizationdataSubmissionView.as_view(), name='org-submission-data'),
    url(r'^proj-submission/(?P<pk>[0-9]+)/(?P<type>[0-9]+)/$', ProjectdataSubmissionView.as_view(), name='proj-submission-data'),
    url(r'^site-submission/(?P<pk>[0-9]+)/(?P<type>[0-9]+)/$', SitedataSubmissionView.as_view(), name='site-submission-data'),
    url(r'^site/report/(?P<pk>\d+)/$', project_html_export, name='site-responses-report'),

    #for Regions

    url(r'^api/project/(?P<pk>\d+)/regions/$', ProjectRegionslistViewSet.as_view({'get': 'list'}), name='project-regions-list'),
    url(r'^region/add/(?P<pk>[0-9]+)/$', RegionCreateView.as_view(), name='region-add'),
    url(r'^region/delete/(?P<pk>[0-9]+)$', RegionDeleteView.as_view(), name='region-delete'),
    url(r'^region/(?P<pk>[0-9]+)$', RegionUpdateView.as_view(), name='region-update'),
    url(r'^region/$', RegionListView.as_view(), name='region-list'),

    url(r'^api/project-regions/(?P<pk>\d+)/$', RegionViewSet.as_view({'get': 'list'}), name='project_regions_api'),
    url(r'^project/(?P<pk>\d+)/regional-sites/(?P<region_pk>\d+)/$', RegionalSitelist.as_view(), name='regional-sites'),
    url(r'^api/project/(?P<pk>\d+)/regional-sites/(?P<region_pk>\d+)/$', SiteUnderRegionViewSet.as_view({'get': 'list'}), name='region-sites-list'),
    url(r'^site/add/(?P<pk>[0-9]+)/(?P<region_pk>[0-9]+)/', RegionalSiteCreateView.as_view(), name='regional-site-add'),

    url(r'^search-org/$', OrganizationSearchView.as_view(), name='search-org-list'),
    url(r'^search-proj/(?P<pk>\d+)/$', ProjectSearchView.as_view(), name='search-proj-list'),

]