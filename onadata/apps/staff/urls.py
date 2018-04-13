from onadata.apps.staff.viewsets.staffViewset import StaffViewSet, AttendanceViewSet, TeamViewSet, StaffUpdateViewSet, staffdesignations, staffgender, BankViewSet

from django.conf.urls import url
from .views import TeamDetail, TeamList, TeamCreate, TeamUpdate, TeamDelete, StaffList,StaffCreate, StaffDetail, StaffDelete,StaffUpdate, StaffProjectCreate, StaffProjectUpdate, StaffProjectList
from . import views
app_name = 'staff'

urlpatterns = [
    url(r'^api/genders/$', staffgender, name='staffgenders'),
    url(r'^api/designations/$', staffdesignations, name='staffdesignations'),
    url(r'^api/banks/$', BankViewSet.as_view({'get': 'list',}), name='bank-list-api'),  
    url(r'^api/myteam/$', TeamViewSet.as_view({'get': 'list',}), name='team-api'),   
    url(r'^api/staff/(?P<team_id>[0-9]+)/$', StaffViewSet.as_view({'get': 'list', 'post': 'create'}), name='staff-list-api'),
    url(r'^api/staff/(?P<team_id>[0-9]+)/detail/(?P<pk>[0-9]+)/$', StaffUpdateViewSet.as_view({'get': 'list', 'post': 'update'}), name='staff-detail-api'),
    url(r'^api/attendance/(?P<team_id>[0-9]+)/$', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance-api'),
    
    url(r'^team-list/(?P<pk>[0-9]+)',TeamList.as_view(), name="team-list"),
    url(r'^team/(?P<pk>[0-9]+)/$',TeamDetail.as_view(), name="team-detail"),
    #url(r'^team/create/$',TeamCreate.as_view(), name="team-create"),
    #url(r'^team/update/(?P<pk>[0-9]+)/$',TeamUpdate.as_view(), name="team-update"),
    #url(r'^team/delete/(?P<pk>[0-9]+)/$',TeamDelete.as_view(), name="team-delete"),
    url(r'^staff-list/(?P<pk>[0-9]+)/$', StaffList.as_view(), name="staff-list"),
    url(r'^staff/(?P<pk>[0-9]+)/$', StaffDetail.as_view(), name="staff-detail"),
    #url(r'^staff/create/$', StaffCreate.as_view(), name="staff-create"),
    url(r'^staff/update/(?P<pk>[0-9]+)/$', StaffUpdate.as_view(), name="staff-update"),
    url(r'^staff/delete/(?P<pk>[0-9]+)/$', StaffDelete.as_view(), name="staff-delete"),
    url(r'^staff-project-list/$', StaffProjectList.as_view(), name="staff-project-list"),
    #gurl(r'^staff-project/create/(?P<pk>[0-9]+)/$', StaffProjectCreate.as_view(), name="staff-project-create"),
    url(r'^staff-project/update/(?P<pk>[0-9]+)/$', StaffProjectUpdate.as_view(), name="staff-project-update"),
    ]