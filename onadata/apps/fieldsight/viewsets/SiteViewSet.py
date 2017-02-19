from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from onadata.apps.fieldsight.models import Site
from onadata.apps.fieldsight.serializers.SiteSerializer import SiteSerializer


class SiteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

    def filter_queryset(self, queryset):
        project = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project, is_active=True)
