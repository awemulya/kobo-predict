from __future__ import unicode_literals
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
from onadata.apps.staff.models import Staff, Attendance, Team, STAFF_TYPES, GENDER_TYPES, Bank
from onadata.apps.staff.serializers.staffSerializer import StaffSerializer, AttendanceSerializer, TeamSerializer, BankSerializer
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
SAFE_METHODS = ('GET', 'POST')


def staffdesignations(request):
    return HttpResponse(json.dumps(STAFF_TYPES), status=200)

def staffgender(request):
    return HttpResponse(json.dumps(GENDER_TYPES), status=200)

class TeamAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated():
            return False
        
        if request.group.name == "Super Admin":
            return True

        team_leader = Team.objects.filter(is_deleted=False, pk=view.kwargs.get('team_id'), leader_id = request.user.id)
        
        if team_leader:
            return True

        return False

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer
    authentication_classes = (BasicAuthentication,)
    def filter_queryset(self, queryset):
        return queryset

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.filter(is_deleted=False)
    serializer_class = TeamSerializer
    authentication_classes = (BasicAuthentication,)
    def filter_queryset(self, queryset):
        try:
            queryset = queryset.filter(leader_id=self.request.user.pk)
            print queryset
        except:
            queryset = []
        return queryset


class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.filter(is_deleted=False)
    serializer_class = StaffSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    # permission_classes = (TeamAccessPermission,)
    # parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        try:
            queryset = queryset.filter(team_id=self.kwargs.get('team_id'))
        except:
            queryset = []
        return queryset

    def perform_create(self, serializer, **kwargs):
        serializer.save(created_by=self.request.user, team_id=self.kwargs.get('team_id'))
        return serializer

class StaffUpdateViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Staff.objects.filter(is_deleted=False)
    serializer_class = StaffSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (TeamAccessPermission,)

    def filter_queryset(self, queryset):

        return queryset.filter(pk=self.kwargs.get('pk', None), team_id=self.kwargs.get('team_id', None))

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceSerializer
    permission_classes = (TeamAccessPermission,)
    authentication_classes = (BasicAuthentication,)

    def filter_queryset(self, queryset):
        try:
            queryset = queryset.filter(team_id=self.request.user.pk)
        except:
            queryset = []
        return queryset

    def perform_create(self, serializer, **kwargs):
        data = serializer.save(submitted_by=self.request.user, team_id=self.kwargs.get('team_id'))
        return data