from django.conf.urls import url
from .views import UserRoleListView, UserRoleDeleteView, UserRoleUpdateView,  UserRoleCreateView, set_role

urlpatterns = [
    url(r'^set-role/(?P<pk>[0-9]+)/$', set_role, name='set_role'),
    url(r'^userroles/$', UserRoleListView.as_view(), name='user-role-list'),
    url(r'^userroles/add/$', UserRoleCreateView.as_view(), name='user-role-add'),
    url(r'^userroles/(?P<pk>[0-9]+)/$', UserRoleUpdateView.as_view(), name='user-role-edit'),
    url(r'^userroles/delete/(?P<pk>\d+)/$', UserRoleDeleteView.as_view(), name='user-role-delete'),
    ]