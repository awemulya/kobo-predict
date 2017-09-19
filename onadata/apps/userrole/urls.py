from onadata.apps.userrole.viewsets.UserRoleViewsets import UserRoleViewSet, MultiOPSlistViewSet, MultiUserAssignRoleViewSet, MultiUserlistViewSet
from .views import UserRoleListView, UserRoleDeleteView, UserRoleUpdateView,  UserRoleCreateView, set_role, UserCreate, \
    remove_role
from django.conf.urls import url

urlpatterns = [
    url(r'^set-role/(?P<pk>[0-9]+)/$', set_role, name='set_role'),
    url(r'^userroles/$', UserRoleListView.as_view(), name='user-role-list'),
    url(r'^userroles/add/$', UserRoleCreateView.as_view(), name='user-role-add'),
    url(r'^userroles/(?P<pk>[0-9]+)/$', UserRoleUpdateView.as_view(), name='user-role-edit'),
    url(r'^userroles/delete/(?P<pk>\d+)/$', UserRoleDeleteView.as_view(), name='user-role-delete'),
    url(r'^user/add$', UserCreate.as_view(), name='user_add'),

    url(r'^api/people/(?P<level>\d)/(?P<pk>\d+)$', UserRoleViewSet.as_view({'post': 'custom_create','get': 'list'})),
    url(r'^api/multiuserassign/(?P<level>\d)/(?P<pk>\d+)$', MultiUserAssignRoleViewSet.as_view(), name="multi_user_assign"),
    url(r'^api/multiuserlist/(?P<level>\d)/(?P<pk>\d+)$', MultiUserlistViewSet.as_view({'get': 'list'}), name="multi_user_list"),
    url(r'^api/multi-ops-list/(?P<level>\d)/(?P<pk>\d+)$', MultiOPSlistViewSet.as_view({'get': 'list'}), name="multi_ops_list"),
    url(r'^api/people/deactivate/$', remove_role, name='remove_role'),
    ]