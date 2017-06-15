from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication

from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission


from onadata.apps.fieldsight.models import Project
from onadata.apps.fieldsight.serializers.ProjectSerializer import ProjectTypeSerializer, ProjectSerializer, ProjectCreationSerializer


class ProjectPermission(BasePermission):
    # def has_permission(self, request, view):
    #     if request.group:
    #         if request.group.name in ["Super Admin", "Organization Admin"]:
    #             return True
    #     return False

    def has_object_permission(self, request, view, obj):
        if request.group:
            if request.group.name == "Super Admin":
                return True
            if request.group.name == "Organization Admin":
                return obj.organization == request.organization
        return False

class ProjectCreationViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectCreationSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (ProjectPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        user = serializer.save()
        project = Project(user=user, organization_id=self.kwargs.get('pk'))
        project.save()
        project.logs.create(source=self.request.user, type=0, title="new User",
                                    organization=project.organization, description="new user {0} created by {1}".
                                    format(user.username, self.request.user.username))



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
    queryset = Project.objects.all()
    serializer_class = ProjectTypeSerializer

    authentication_classes = (BasicAuthentication,)
    permission_classes = (ProjectPermission,)

    def filter_queryset(self, queryset):
        id = self.kwargs.get('pk', None)
        return queryset.filter(organization__id=id, is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}


class OrganizationsProjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing projects Under Organizations.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    authentication_classes = (BasicAuthentication,)
    permission_classes = (ProjectPermission,)

    def filter_queryset(self, queryset):

        id = self.kwargs.get('pk', None)
        return queryset.filter(organization__id=id, is_active=True)



    # authentication_classes = (BasicAuthentication,)
    permission_classes = (ProjectsPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(organization__pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}
