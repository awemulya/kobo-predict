from onadata.apps.staff.viewsets.staffViewset import StaffViewSet, StafflistViewSet, AttendanceViewSet, TeamViewSet, StaffUpdateViewSet, staffdesignations, staffgender, BankViewSet

from django.conf.urls import url
from .views import TeamDetail, TeamReAssignStaff, TeamStaffsapi,  TeamAttendanceReport, TeamList, TeamCreate, TeamUpdate, TeamDelete, StaffList, StaffAttendanceUpdate, StaffCreate, StaffDetail, StaffDelete,StaffUpdate, StaffProjectCreate, StaffProjectUpdate, StaffProjectList, StaffProjectDetail
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
    url(r'^api/team/staff/(?P<team_id>[0-9]+)/$',StafflistViewSet.as_view({'get':'list'}), name="api-staffs"),
    
    url(r'^team-list/(?P<pk>[0-9]+)',TeamList.as_view(), name="team-list"),
    url(r'^team/(?P<pk>[0-9]+)/$',TeamDetail.as_view(), name="team-detail"),
    url(r'^team/create/(?P<pk>[0-9]+)/$',TeamCreate.as_view(), name="team-create"),
    url(r'^team/reassign-staff/(?P<pk>[0-9]+)/(?P<team_id>[0-9]+)/$',TeamReAssignStaff.as_view(), name="team-reassign-staffs"),
    url(r'^team/update/(?P<pk>[0-9]+)/$',TeamUpdate.as_view(), name="team-update"),
    url(r'^team/delete/(?P<pk>[0-9]+)/$',TeamDelete.as_view(), name="team-delete"),
    url(r'^staff-list/(?P<pk>[0-9]+)/$', StaffList.as_view(), name="staff-list"),
    url(r'^staff/(?P<pk>[0-9]+)/$', StaffDetail.as_view(), name="staff-detail"),
    url(r'^staff/create/(?P<pk>[0-9]+)/$', StaffCreate.as_view(), name="staff-create"),
    url(r'^staff/update/(?P<pk>[0-9]+)/$', StaffUpdate.as_view(), name="staff-update"),
    url(r'^staff/delete/(?P<pk>[0-9]+)/$', StaffDelete.as_view(), name="staff-delete"),
    url(r'^staff-project-list/$', StaffProjectList.as_view(), name="staff-project-list"),
    url(r'^staff-project/create/$', StaffProjectCreate.as_view(), name="staff-project-create"),

    url(r'^staff-project/(?P<pk>[0-9]+)/$', StaffProjectDetail.as_view(), name="staff-project-detail"),

    url(r'^staff-project/update/(?P<pk>[0-9]+)/$', StaffProjectUpdate.as_view(), name="staff-project-update"),
    url(r'^attendance/update/(?P<pk>[0-9]+)/(?P<date>\d{4}-\d{2}-\d{2})/$', StaffAttendanceUpdate.as_view(), name="staff-attendance-update"),
    
    url(r'^team-attendance/(?P<pk>[0-9]+)/(?P<date>\d{4}-\d{2})/$', TeamAttendanceReport.as_view(), name="team-attendance-report"),

    ]