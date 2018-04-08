from onadata.apps.staff.viewsets.staffViewset import StaffViewSet, AttendanceViewSet, TeamViewSet

from django.conf.urls import url

urlpatterns = [
    url(r'^api/myteam/$', TeamViewSet.as_view({'get': 'list',}), name='team-api'),   
    url(r'^api/staff/(?P<team_id>[0-9]+)/$', StaffViewSet.as_view({'get': 'list', 'post': 'create'}), name='staff-api'),
    url(r'^api/attendance/(?P<team_id>[0-9]+)/$', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance-api'),
    ]