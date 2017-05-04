from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission

from onadata.apps.fieldsight.models import ProjectType, Project
from onadata.apps.fieldsight.serializers.ProjectSerializer import ProjectTypeSerializer, ProjectSerializer


class ProjectsPermission(BasePermission):
    def has_permission(self, request, view):
        return request.group.name in ["Super Admin", "Organization Admin" ]

    def has_object_permission(self, request, view, obj):
        if request.group.name == "Organization Admin":
            return obj.organization == request.organization


class ProjectTypeViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing project and site  type.
    """
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer


class OrganizationsProjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing projects Under Organizations.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    # authentication_classes = (BasicAuthentication,)
    permission_classes = (ProjectsPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(organization__pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}
