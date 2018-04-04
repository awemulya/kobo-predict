from onadata.apps.staff.viewsets.staffViewset import StaffViewSet, AttendanceViewSet

from django.conf.urls import url

urlpatterns = [
    url(r'^api/staff/$', StaffViewSet.as_view({'get': 'list', 'post': 'create'}), name='staff-api'),
    url(r'^api/attendence/$', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance-api'),
    ]