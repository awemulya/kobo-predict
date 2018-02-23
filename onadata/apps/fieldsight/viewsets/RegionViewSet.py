from rest_framework import viewsets
from django.db.models import Q

from onadata.apps.fieldsight.models import Region
from onadata.apps.fieldsight.serializers.RegionSerializer import RegionSerializer
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

class RegionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

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
        return self.queryset.filter(Q(name__icontains=query) | Q(identifier__icontains=query))


