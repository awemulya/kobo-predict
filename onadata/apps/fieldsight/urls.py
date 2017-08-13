from django.conf.urls import url
from fcm.views import DeviceViewSet
from onadata.apps.fieldsight.viewsets.FieldsightFcmViewset import FcmDeviceViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import OrganizationsProjectViewSet

from onadata.apps.fieldsight.viewsets.OrganizationViewset import OrganizationTypeViewSet, OrganizationViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import ProjectTypeViewSet, ProjectCreationViewSet

from onadata.apps.fieldsight.viewsets.ProjectViewSet import OrganizationsProjectViewSet

from onadata.apps.fieldsight.viewsets.SiteViewSet import SiteViewSet, AllSiteViewSet, SiteCreationSurveyViewSet, \
    SiteReviewViewSet, ProjectTypeViewset, SiteReviewUpdateViewSet, SiteUnderProjectViewSet
from .forms import RegistrationForm

from .views import (
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
    UserListView, site_images, FilterUserView, upload_sites, blue_prints, add_project_role, ManagePeopleSiteView,
    ManagePeopleProjectView, ManagePeopleOrganizationView, site_survey_list, ajax_upload_sites, ajax_save_site,
    ajax_save_project, RolesView, OrgProjectList, OrgUserList, ProjUserList, SiteUserList)


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
    url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^project-dashboard/(?P<pk>[0-9]+)/$', Project_dashboard.as_view(), name='project-dashboard'),
    url(r'^api/org-projects/(?P<pk>\d+)/$', OrganizationsProjectViewSet.as_view({'get': 'list'})),
    url(r'^api/async_save_project/$', ajax_save_project),

    url(r'^org-projects/(?P<pk>\d+)/$', OrgProjectList.as_view(), name='org-project-list'),
    url(r'^org-users/(?P<pk>\d+)/$', OrgUserList.as_view(), name='org-user-list'),
    url(r'^proj-users/(?P<pk>\d+)/$', ProjUserList.as_view(), name='proj-user-list'),
    url(r'^site-users/(?P<pk>\d+)/$', SiteUserList.as_view(), name='site-user-list'),


    url(r'^upload/(?P<pk>\d+)/$', upload_sites, name='site-upload'),
    url(r'^api/bulk_upload_site/(?P<pk>\d+)/$', ajax_upload_sites),
    url(r'^api/async_save_site/(?P<pk>\d+)/$', ajax_save_site),
    url(r'^project/delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),
    url(r'^project/alter-status/(?P<pk>\d+)/$', alter_proj_status, name='alter_proj_status'),
    url(r'^project/add-proj-manager/(?P<pk>\d+)/$', add_proj_manager, name='add_proj_manager'),
    url(r'^project/add-role/(?P<pk>\d+)/$', add_project_role, name='add_project_staffs'),
    url(r'^api/project-sites/(?P<pk>\d+)/$', SiteViewSet.as_view({'get': 'list'}), name='project_sites'),


    url(r'^survey-sites/(?P<pk>\d+)$', site_survey_list, name='site-survey-list'),
    url(r'^api/sites/$', AllSiteViewSet.as_view({'get': 'list'}), name='sites-list'),
    url(r'^api/project-types/$', ProjectTypeViewset.as_view({'get': 'list'})),
    url(r'^api/survey-sites/(?P<pk>\d+)/$', SiteCreationSurveyViewSet.as_view({'get': 'list'}), name='sites-list'),
    url(r'^api/survey-sites-review/(?P<pk>\d+)/$', SiteReviewViewSet.as_view({'get': 'list'}), name='sites-list-review'),
    url(r'^api/project-sites/(?P<pk>\d+)/$', SiteUnderProjectViewSet.as_view({'get': 'list'}), name='project-sites-list'),
    url(r'^api/survey-sites-review-update/(?P<pk>\d+)/$', SiteReviewUpdateViewSet.as_view({'post': 'update'})),
    url(r'^api/survey-sites/$', SiteCreationSurveyViewSet.as_view({'post': 'create', 'put':'update'}), name='sites-list'),
    url(r'^site/$', SiteListView.as_view(), name='sites-list'),
    url(r'^site/$', SiteListView.as_view(), name='site-list'),
    url(r'^site/add/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^site/(?P<pk>[0-9]+)/$', SiteUpdateView.as_view(), name='site-edit'),
    url(r'^site/blue-prints/(?P<id>[0-9]+)/$', blue_prints, name='site-blue-prints'),
    url(r'^site-dashboard/(?P<pk>[0-9]+)/$', SiteDashboardView.as_view(), name='site-dashboard'),

    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),
    url(r'^site/alter-status/(?P<pk>\d+)/$', alter_site_status, name='alter_site_status'),
    url(r'^site/add-supervisor/(?P<pk>\d+)/$', add_supervisor, name='add_supervisor'),
    url(r'^api/site-images/(?P<pk>\d+)/$', site_images, name='site_images'),

    url(r'^manage/people/site/(?P<pk>\d+)/$', ManagePeopleSiteView.as_view(), name='manage-people-site'),
    url(r'^manage/people/project/(?P<pk>\d+)/$', ManagePeopleProjectView.as_view(), name='manage-people-project'),
    url(r'^manage/people/organization/(?P<pk>\d+)/$', ManagePeopleOrganizationView.as_view(), name='manage-people-organization'),

    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
    url(r'^filter-users/$', FilterUserView.as_view(), name='filter-users'),
    url(r'fcm/v1/devices/$', DeviceViewSet.as_view({'get': 'list'})),
    url(r'fcm/add/', FcmDeviceViewSet.as_view({'post': 'create'})),
    url(r'fcm/logout/', FcmDeviceViewSet.as_view({'post': 'inactivate'})),
    url(r'myroles/', RolesView.as_view(), name='roles-dashboard'),

]
   


