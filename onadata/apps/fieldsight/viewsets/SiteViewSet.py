from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, BasePermission

from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fieldsight.models import Site
from onadata.apps.fieldsight.serializers.SiteSerializer import SiteSerializer, SiteCreationSurveySerializer
from onadata.apps.userrole.models import UserRole


class SiteSurveyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_survey:
            return False
        return request.project == obj.project


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
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = SiteSerializer

    def filter_queryset(self, queryset):
        if self.request.role.group.name == "Super Admin":
            return queryset
        elif self.request.role.group.name == "Organization Admin":
            return queryset.filter(project__organization=self.request.organization, is_active=True)
        elif self.request.role.group.name == "Project Manager":
            return queryset.filter(project=self.request.project, is_active=True)
        elif self.request.role.group.name == "Reviewer":
            return queryset.filter(pk__in=[role.site.id for role in UserRole.objects.filter(
                group=self.request.role.group, user=self.request.role.user)])
        return []


class SiteCreationSurveyViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_survey=True)
    serializer_class = SiteCreationSurveySerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteSurveyPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}
