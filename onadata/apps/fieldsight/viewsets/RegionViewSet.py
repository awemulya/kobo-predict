from rest_framework import viewsets

from onadata.apps.fieldsight.models import Region
from onadata.apps.fieldsight.serializers.RegionSerializer import RegionSerializer
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin
from rest_framework.permissions import BasePermission


class RegionViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing organization.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)