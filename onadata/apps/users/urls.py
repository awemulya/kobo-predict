from django.conf.urls import url

from onadata.apps.users.views import ContactViewSet, UsersListView
from onadata.apps.users.viewsets import UserViewSet, ProfileViewSet, UserListViewSet, SearchableUserListViewSet
from . import views
urlpatterns = [
    url(r'^$', UsersListView.as_view(), name='users'),
    url(r'^api/list/all(?:/(?P<level>[1-4]))?(?:/(?P<username>[^/]+))?/$', SearchableUserListViewSet.as_view({'get': 'list'})),
    url(r'^contacts/$', ContactViewSet.as_view({'get': 'list'}), name='contacts'),
    url(r'^list/(?P<pk>[0-9]+)/$', UserViewSet.as_view({'get': 'list','post': 'create',}), name='user'),
    url(r'^api/list/(?P<pk>[0-9]+)/$', UserListViewSet.as_view({'get': 'list'}), name='user-list'),
    url(r'^contacts/(?P<pk>[0-9]+)/$', ContactViewSet.as_view({'get': 'list'}), name='project_contacts'),
    url(r'^me/', views.current_user, name='current_user'),
    url(r'^alter-status/(?P<pk>[0-9]+)/$', views.alter_status, name='alter_status'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.edit, name='edit'),
    url(r'^api/alter-status/(?P<pk>[0-9]+)/$', views.alter_status),
    url(r'^api/get-auth-token/$', views.ObtainAuthToken.as_view() ),
    url(r'^profile-update/(?P<pk>[0-9]+)/$', views.ProfileUpdateView.as_view(), name='profile_update'),
    url(r'^api/profile(?:/(?P<pk>[0-9]+))?/$',
        ProfileViewSet.as_view({'put': 'update','get':'retrieve'}), name='profile_update_api'),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.my_profile, name='profile'),
    ]

