from rest_framework import viewsets

from onadata.apps.fieldsight.models import Region
from onadata.apps.fieldsight.serializers.RegionSerializer import RegionSerializer
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin
from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination


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
    page_size = 20


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

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)

    def get_queryset(self):
        query = self.request.REQUEST.get("q")
        return self.queryset.filter(name__icontains=query)

