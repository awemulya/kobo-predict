from onadata.apps.staff.viewsets.staffViewset import StaffViewSet, AttendanceViewSet, TeamViewSet, StaffUpdateViewSet, staffdesignations, staffgender, BankViewSet

from django.conf.urls import url

urlpatterns = [
    url(r'^api/genders/$', staffgender, name='staffgenders'),
    url(r'^api/designations/$', staffdesignations, name='staffdesignations'),
    url(r'^api/banks/$', BankViewSet.as_view({'get': 'list',}), name='bank-list-api'),  
    url(r'^api/myteam/$', TeamViewSet.as_view({'get': 'list',}), name='team-api'),   
    url(r'^api/staff/(?P<team_id>[0-9]+)/$', StaffViewSet.as_view({'get': 'list', 'post': 'create'}), name='staff-list-api'),
    url(r'^api/staff/(?P<team_id>[0-9]+)/detail/(?P<pk>[0-9]+)/$', StaffUpdateViewSet.as_view({'get': 'list', 'post': 'update'}), name='staff-detail-api'),
    url(r'^api/attendance/(?P<team_id>[0-9]+)/$', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance-api'),
    ]