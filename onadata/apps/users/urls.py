from django.conf.urls import url

from onadata.apps.users.views import ContactViewSet, UsersListView, MyProfile, EndUserRole, web_login, web_signup, \
    send_request_for_organization, request_organization, approve_organization, deny_organization
from onadata.apps.users.viewsets import UserViewSet, ProfileViewSet, UserListViewSet, SearchableUserListViewSet, \
    MySitesViewset, MySitesOnlyViewset, MyProjectsViewset
from . import views


urlpatterns = [

    url(r'^accounts/login/', web_login, name='web_login'),
    url(r'^signup/', web_signup, name='web_signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^approve-organization/(?P<username>[^/]+)?/(?P<org_id>[0-9]+)/$', approve_organization, name='approve_organization'),
    url(r'^deny-organization/(?P<org_id>[0-9]+)/(?P<username>[^/]+)?/$', deny_organization, name='deny_organization'),

    url(r'^send-request-organization/(?P<org_id>[0-9]+)/$', send_request_for_organization, name='send_request_organization'),
    url(r'^request-organization/(?P<org_id>[0-9]+)/(?P<sender>[^/]+)?/$', request_organization, name='request_organization'),

    url(r'^$', UsersListView.as_view(), name='users'),
    url(r'^api/list/all(?:/(?P<level>[1-4]))?(?:/(?P<username>[^/]+))?/$', SearchableUserListViewSet.as_view({'get': 'list'})),
    url(r'^contacts/$', ContactViewSet.as_view({'get': 'list'}), name='contacts'),
    url(r'^list/(?P<pk>[0-9]+)/$', UserViewSet.as_view({'get': 'list','post': 'create',}), name='user'),
    url(r'^api/list/(?P<pk>[0-9]+)/$', UserListViewSet.as_view({'get': 'list'}), name='user-list'),
    url(r'^contacts/(?P<pk>[0-9]+)/$', ContactViewSet.as_view({'get': 'list'}), name='project_contacts'),
    url(r'^me/', views.current_user, name='current_user'),
    url(r'^metwo/', views.current_usertwo, name='current_usertwo'),
    url(r'^mysites/', MySitesViewset.as_view({'get': 'list'}), name='msvs'),
    url(r'^mysitesonly/', MySitesOnlyViewset.as_view({'get': 'list'}), name='msovs'),
    url(r'^myprojects/', MyProjectsViewset.as_view({'get': 'list'}), name='mpvs'),
    url(r'^alter-status/(?P<pk>[0-9]+)/$', views.alter_status, name='alter_status'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.edit, name='edit'),
    url(r'^api/alter-status/(?P<pk>[0-9]+)/$', views.alter_status),
    url(r'^api/get-auth-token/$', views.ObtainAuthToken.as_view() ),
    url(r'^profile-update/(?P<pk>[0-9]+)/$', views.ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^api/profile/(?P<pk>[0-9]+)/$',
        ProfileViewSet.as_view({'post': 'update'}), name='profile_update_api'),
    url(r'^api/profile(?:/(?P<pk>[0-9]+))?/$',
        ProfileViewSet.as_view({'get':'retrieve'}), name='profile_get_api'),

    url(r'^profile/(?P<pk>[0-9]+)/$', MyProfile.as_view(), name='profile'),
    url(r'^endrole/(?P<pk>[0-9]+)/$', EndUserRole.as_view(), name='end_user_role'),
    ]
