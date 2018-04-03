import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission

from django.db.models import Q
from django.views.generic import View
from django.http import HttpResponse
from onadata.apps.staff.models import Staff, Attendance
from onadata.apps.staff.serializers.staffSerializer import StaffSerializer, AttendanceSerializer

SAFE_METHODS = ('GET', 'POST')

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

    def filter_queryset(self, queryset):
        try:
            queryset = queryset.filter(team_leader_id=self.request.user.pk)
        except:
            queryset = []
        return queryset

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def filter_queryset(self, queryset):
        try:
            queryset = queryset.filter(team_leader_id=self.request.user.pk)
        except:
            queryset = []
        return queryset
