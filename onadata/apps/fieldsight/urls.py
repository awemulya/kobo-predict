from django.conf.urls import url
from .forms import RegistrationForm

from .views import (
    dashboard,
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDeleteView,
    alter_org_status,
    add_org_admin,
    ProjectListView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    alter_proj_status,
    add_proj_manager,
    SiteListView,
    SiteCreateView,
    SiteUpdateView,
    SiteDeleteView,
    alter_site_status,
    add_supervisor,
    add_central_engineer,
    CreateUserView,
    UserListView,
    UserRoleListView,
    UserRoleDeleteView,
    UserRoleUpdateView,
    UserRoleCreateView,
)



urlpatterns = [
    # group_required('superuser')(OrgView.as_view())
    # dispatch or get_context_data to control only org admin or that orf can actions on its projects and sites.
    # url(r'^$', dashboard, name='dashboard'),
    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),

    url(r'^organization/$', OrganizationListView.as_view(), name='organization-list'),
    url(r'^organization/add/$', OrganizationCreateView.as_view(), name='organization-add'),
    url(r'^organization/(?P<pk>[0-9]+)/$', OrganizationUpdateView.as_view(), name='organization-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^organization/delete/(?P<pk>\d+)/$', OrganizationDeleteView.as_view(), name='organization-delete'),
    url(r'^organization/alter-status/(?P<pk>\d+)/$', alter_org_status, name='alter_org_status'),
    url(r'^organization/add-org-admin/(?P<pk>\d+)/$', add_org_admin, name='add_org_admin'),

    url(r'^project/$', ProjectListView.as_view(), name='project-list'),
    url(r'^project/add/$', ProjectCreateView.as_view(), name='project-add'),
    url(r'^project/(?P<pk>[0-9]+)/$', ProjectUpdateView.as_view(), name='project-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^project/delete/(?P<pk>\d+)/$', ProjectDeleteView.as_view(), name='project-delete'),
    url(r'^project/alter-status/(?P<pk>\d+)/$', alter_proj_status, name='alter_proj_status'),
    url(r'^project/add-proj-admin/(?P<pk>\d+)/$', add_proj_manager, name='add_proj_manager'),


    url(r'^site/$', SiteListView.as_view(), name='site-list'),
    url(r'^site/add/$', SiteCreateView.as_view(), name='site-add'),
    url(r'^site/(?P<pk>[0-9]+)/$', SiteUpdateView.as_view(), name='site-edit'),
    # url(r'^organization/search/$', organization_search, name='search-org'),
    url(r'^site/delete/(?P<pk>\d+)/$', SiteDeleteView.as_view(), name='site-delete'),
    url(r'^site/alter-status/(?P<pk>\d+)/$', alter_site_status, name='alter_site_status'),
    url(r'^site/add-central-engineer/(?P<pk>\d+)/$', add_central_engineer, name='add_central_engineer'),
    url(r'^site/add-supervisor/(?P<pk>\d+)/$', add_supervisor, name='add_supervisor'),

    url(r'^userroles/$', UserRoleListView.as_view(), name='user-role-list'),
    url(r'^userroles/add/$', UserRoleCreateView.as_view(), name='user-role-add'),
    url(r'^userroles/(?P<pk>[0-9]+)/$', UserRoleUpdateView.as_view(), name='user-role-edit'),
    url(r'^userroles/delete/(?P<pk>\d+)/$', UserRoleDeleteView.as_view(), name='user-role-delete'),

    url(r'^accounts/create/$', CreateUserView.as_view(
        form_class=RegistrationForm), name='user-create'),
    url(r'^userlist/$', UserListView.as_view(), name='user-list'),
]
