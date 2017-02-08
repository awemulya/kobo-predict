from django.conf.urls import url, include
from rest_framework import routers

from onadata.apps.fieldsight.viewsets.OrganizationViewset import OrganizationTypeViewSet, OrganizationViewSet
from onadata.apps.fieldsight.viewsets.ProjectViewSet import ProjectTypeViewSet, ProjectViewSet
from onadata.apps.fieldsight.viewsets.SiteViewSet import SiteViewSet
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
    add_central_engineer,
    CreateUserView,
    UserListView, site_images, filter_users)

router = routers.SimpleRouter()
# router.register(r'api/organization-type', OrganizationTypeViewSet)
# router.register(r'api/organization', OrganizationViewSet)
# router.register(r'api/project-type', ProjectTypeViewSet)
# router.register(r'api/project', ProjectViewSet)
# router.register(r'api/site', SiteViewSet)


urlpatterns = [
    # group_required('superuser')(OrgView.as_view())
    # dispatch or get_context_data to control only org admin or that orf can actions on its projects and sites.
    # url(r'^$', dashboard, name='dashboard'),
    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),

    url(r'^organization/$', OrganizationListView.as_view(), name='organizations-list'),
    url(r'^organization/$', OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/add/$', OrganizationCreateView.as_view(), name='organization-add'),
    url(r'^organization/(?P<pk>[0-9]+)/$', OrganizationUpdateView.as_view(), name='organization-edit'),
    url(r'^organization-dashboard/(?P<pk>[0-9]+)/$', organization_dashboard, name='organization-dashboard'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^organization/delete/(?P<pk>\d+)/$', OrganizationDeleteView.as_view(), name='organization-delete'),
    url(r'^organization/alter-status/(?P<pk>\d+)/$', alter_org_status, name='alter_org_status'),
    url(r'^organization/add-org-admin/(?P<pk>\d+)/$', add_org_admin, name='add_org_admin'),

    url(r'^project/$', ProjectListView.as_view(), name='projects-list'),
    url(r'^project/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    url(r'^project-dashboard/(?P<pk>[0-9]+)/$', project_dashboard, name='project-dashboard'),


    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^project/delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),
    url(r'^project/alter-status/(?P<pk>\d+)/$', alter_proj_status, name='alter_proj_status'),
    url(r'^project/add-proj-manager/(?P<pk>\d+)/$', add_proj_manager, name='add_proj_manager'),
    url(r'^project/add-central-engineer/(?P<pk>\d+)/$', add_central_engineer, name='add_central_engineer'),



    url(r'^site/$', SiteListView.as_view(), name='sites-list'),
    url(r'^site/$', SiteListView.as_view(), name='site-list'),
    url(r'^site/add/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^site/(?P<pk>[0-9]+)/$', SiteUpdateView.as_view(), name='site-edit'),
    url(r'^site-dashboard/(?P<pk>[0-9]+)/$', site_dashboard, name='site-dashboard'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),
    url(r'^site/alter-status/(?P<pk>\d+)/$', alter_site_status, name='alter_site_status'),
    url(r'^site/add-supervisor/(?P<pk>\d+)/$', add_supervisor, name='add_supervisor'),
    url(r'^api/site-images/(?P<pk>\d+)/$', site_images, name='site_images'),


    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
    url(r'^filter-users/$', filter_users, name='filter-users'),
    url(r'fcm/', include('fcm.urls')),

    # kobo form
]



urlpatterns += router.urls

