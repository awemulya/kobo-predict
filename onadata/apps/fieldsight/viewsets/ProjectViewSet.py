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
from onadata.apps.geo.models import GeoLayer
from onadata.apps.geo.serializers.GeoSerializer import GeoLayerSerializer

from onadata.apps.fieldsight.models import Project, Region
from onadata.apps.fieldsight.serializers.ProjectSerializer import ProjectMapDataSerializer, ProjectMinimalSerializer, ProjectFormsSerializer, ProjectMetasSerializer, ProjectTypeSerializer, ProjectMiniSerializer, ProjectSerializer, ProjectCreationSerializer
from onadata.apps.fieldsight.serializers.RegionSerializer import RegionSerializer
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.userrole.models import UserRole
from django.db.models import Q

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
                                       organization=project.organization, content_object=project,
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
        return queryset.filter(organization__id=id)

    def get_serializer_context(self):
        return {'request': self.request}



class MyProjectlistViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing Regions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectMiniSerializer

    def filter_queryset(self, queryset):
        if self.request.group.name == "Super Admin":
            return queryset

        user_id = self.kwargs.get('pk', None)
        exclude_pk = self.kwargs.get('exclude_pk', 0)
        project_ids = self.request.roles.filter(group_id=2).values('project_id')
        org_ids = self.request.roles.filter(group_id=1).values('organization_id')
        return queryset.filter(Q(pk__in=project_ids) | Q(organization_id__in=org_ids)).exclude(pk=exclude_pk)


class MyOrgProjectlistViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing Regions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectMiniSerializer

    def filter_queryset(self, queryset):

        exclude_pk = self.kwargs.get('exclude_pk', 0)
        org_id = self.kwargs.get('pk', None)
        return queryset.filter(organization_id=org_id).exclude(pk=exclude_pk)


class ProjectRegionslistViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing Regions.
    """

    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def filter_queryset(self, queryset):
        id = self.kwargs.get('pk', None)
        return queryset.filter(project_id=id)

    def get_serializer_context(self):
        return {'request': self.request}


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })


class ProjectMetas(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing Regions.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectMetasSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk'))

class ProjectForms(viewsets.ModelViewSet):

    queryset = FieldSightXF.objects.filter(is_deleted=False, is_survey=False)
    serializer_class = ProjectFormsSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(project_id=self.kwargs.get('pk'))


class UserProjectlistMinimalViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectMinimalSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (RegionAccessPermission,)

    def filter_queryset(self, queryset):
        projects = UserRole.objects.filter(site__isnull=False, user_id=self.kwargs.get('user_id'), group_id=self.kwargs.get('group_id'), ended_at=None).distinct('project_id').values('project_id') 
        return queryset.filter(id__in=projects)


class DonorMyProjects(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectMapDataSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    def filter_queryset(self, queryset):
        projects = UserRole.objects.filter(user_id=self.request.user.id, project__isnull=False, group_id=7, ended_at=None).distinct('project_id').values('project_id')
        return queryset.filter(pk__in=projects)

class DonorMyProjectsLayers(viewsets.ModelViewSet):
    queryset = GeoLayer.objects.all()
    serializer_class = GeoLayerSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    
    def filter_queryset(self, queryset):
        projects = UserRole.objects.filter(user_id=self.request.user.id, project__isnull=False, group_id=7, ended_at=None).distinct('project_id').values('project_id')
        
        geolayer_ids = []

        donorprojects = Project.objects.filter(pk__in = projects)
        
        for project in donorprojects:
            for layer in project.geo_layers.all():
                geolayer_ids.append(layer.id)
        
        return queryset.filter(pk__in=geolayer_ids)