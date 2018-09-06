from rest_framework import viewsets
from django.db.models import Q

from onadata.apps.fieldsight.models import Region
from onadata.apps.fieldsight.serializers.RegionSerializer import RegionSerializer, AllMainRegionSerializer
from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import BasePermission
from onadata.apps.userrole.models import UserRole
from django.db.models import Q


class RegionAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return True
        if request.group.name == "Project Manager":
            return True
        return False


class RegionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (RegionAccessPermission,)

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 2


class RegionPagignatedViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)


class RegionSearchViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)

    def get_queryset(self):
        query = self.request.GET.get("q")
        return self.queryset.filter(Q(name__icontains=query) |
                                    Q(identifier__icontains=query))


class UserMainRegionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (RegionAccessPermission,)

    def filter_queryset(self, queryset):
        # projects = UserRole.objects.filter(project_id=self.kwargs.get('pk'), user_id=self.kwargs.get('user_id'), ended_at=None).values('project_id') 
        return queryset.filter(project__id=self.kwargs.get('pk'))