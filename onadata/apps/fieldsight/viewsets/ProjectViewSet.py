import json

from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission
from django.http import HttpResponseRedirect, JsonResponse
from channels import Group as ChannelGroup
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

    queryset = Project.objects.all()
    serializer_class = ProjectCreationSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (ProjectPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        project = serializer.save()
        # project.save()
        noti = project.logs.create(source=self.request.user, type=10, title="new Project",
                                       organization=project.organization,
                                       description='{0} created new project named {1}'.format(
                                           self.request.user.get_full_name(), project.name))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        ChannelGroup("notify-{}".format(project.organization.id)).send({"text": json.dumps(result)})
        return project


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
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        id = self.kwargs.get('pk', None)
        return queryset.filter(organization__id=id, is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })