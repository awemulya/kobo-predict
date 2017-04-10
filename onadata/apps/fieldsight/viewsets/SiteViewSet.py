from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from onadata.apps.fieldsight.models import Site
from onadata.apps.fieldsight.serializers.SiteSerializer import SiteSerializer
from onadata.apps.userrole.models import UserRole


class SiteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

    def filter_queryset(self, queryset):
        project = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project, is_active=True)


class AllSiteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer

    def filter_queryset(self, queryset):
        if self.request.role.group.name == "Super Admin":
            return queryset
        elif self.request.role.group.name == "Organization Admin":
            return queryset.filter(project__organization=self.request.project, is_active=True)
        elif self.request.role.group.name == "Project Manager":
            return queryset.filter(project=self.request.project, is_active=True)
        elif self.request.role.group.name == "Reviewer":
            return queryset.filter(pk__in=[role.site.id for role in UserRole.objects.filter(
                group=self.request.role.group, user=self.request.role.user)])
        return []

