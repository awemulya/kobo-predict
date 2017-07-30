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
    organization_dashboard,
    alter_org_status,
    add_org_admin,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    project_dashboard,
    alter_proj_status,
    add_proj_manager,
    SiteListView,
    SiteCreateView,
    SiteUpdateView,
    SiteDeleteView,
    site_dashboard,
    alter_site_status,
    add_supervisor,
    CreateUserView,
    UserListView, site_images, filter_users, upload_sites, blue_prints, add_project_role, manage_people_site,
    manage_people_project, manage_people_organization, site_survey_list, ajax_upload_sites, ajax_save_site,
    ajax_save_project)


urlpatterns = [
    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),

    url(r'^organization/$', OrganizationListView.as_view(), name='organizations-list'),
    url(r'^organization/$', OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/add/$', OrganizationCreateView.as_view(), name='organization-add'),
    url(r'^organization/(?P<pk>[0-9]+)/$', OrganizationUpdateView.as_view(), name='organization-edit'),
    url(r'^organization-dashboard/(?P<pk>[0-9]+)/$', organization_dashboard, name='organizations-dashboard'),
    url(r'^organization/delete/(?P<pk>\d+)/$', OrganizationDeleteView.as_view(), name='organization-delete'),
    url(r'^organization/alter-status/(?P<pk>\d+)/$', alter_org_status, name='alter_org_status'),
    url(r'^organization/add-org-admin/(?P<pk>\d+)/$', add_org_admin, name='add_org_admin'),

    url(r'^api/projects/(?P<pk>\d+)/$', ProjectCreationViewSet.as_view({'get': 'list'}), name='projects-list'),
    url(r'^api/projects/$', ProjectCreationViewSet.as_view({'post': 'create', 'put': 'update'}), name='projects-list'),
    url(r'^project/$', ProjectListView.as_view(), name='projects-list'),
    url(r'^project/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^project-dashboard/(?P<pk>[0-9]+)/$', project_dashboard, name='project-dashboard'),
    url(r'^api/org-projects/(?P<pk>\d+)/$', OrganizationsProjectViewSet.as_view({'get': 'list'})),
    url(r'^api/async_save_project/$', ajax_save_project),


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
    url(r'^site-dashboard/(?P<pk>[0-9]+)/$', site_dashboard, name='site-dashboard'),

    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),
    url(r'^site/alter-status/(?P<pk>\d+)/$', alter_site_status, name='alter_site_status'),
    url(r'^site/add-supervisor/(?P<pk>\d+)/$', add_supervisor, name='add_supervisor'),
    url(r'^api/site-images/(?P<pk>\d+)/$', site_images, name='site_images'),

    url(r'^manage/people/site/(?P<pk>\d+)/$', manage_people_site, name='manage-people-site'),
    url(r'^manage/people/project/(?P<pk>\d+)/$', manage_people_project, name='manage-people-project'),
    url(r'^manage/people/organization/(?P<pk>\d+)/$', manage_people_organization, name='manage-people-organization'),

    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
    url(r'^filter-users/$', filter_users, name='filter-users'),
    url(r'fcm/v1/devices/$', DeviceViewSet.as_view({'get': 'list'})),
    url(r'fcm/add/', FcmDeviceViewSet.as_view({'post': 'create'})),
    url(r'fcm/logout/', FcmDeviceViewSet.as_view({'post': 'inactivate'})),

]


