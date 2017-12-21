import json
from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission

from channels import Group as ChannelGroup


from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fieldsight.models import Site, ProjectType, Project
from onadata.apps.fieldsight.serializers.SiteSerializer import MinimalSiteSerializer, SiteSerializer, SiteCreationSurveySerializer, \
    SiteReviewSerializer, ProjectTypeSerializer, SiteUpdateSerializer, ProjectUpdateSerializer
from onadata.apps.userrole.models import UserRole
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework.pagination import PageNumberPagination

class SiteSurveyPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_survey:
            return False
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return obj.project.organization == request.organization
        return request.project == obj.project


class AllSiteViewPermission(BasePermission):
    def has_permission(self, request, view):
        return request.group.name in ["Super Admin", "Organization Admin", "Project Manager", "Reviewer"]


class SiteUnderProjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj.is_survey:
            return True
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return obj.project.organization == request.organization
        return request.project == obj.project


class SiteSurveyUpdatePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return obj.project.organization == request.organization
        return obj.project == request.project


class SiteViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return obj.project.organization == request.organization
        return obj.project == request.project


class ProjectViewPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.group.name == "Super Admin":
            return True
        if request.group.name == "Organization Admin":
            return obj.project.organization == request.organization
        return request.project == obj.project


class SiteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteViewPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        project = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project, is_active=True)

    def get_serializer_context(self):
        return {'request': self.request}


class SiteUpdateViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.all()
    serializer_class = SiteUpdateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (SiteViewPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}


class ProjectUpdateViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectUpdateSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    # permission_classes = (SiteViewPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}


class AllSiteViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = SiteSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (AllSiteViewPermission,)
    parser_classes = (MultiPartParser, FormParser,)

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

    def perform_create(self, serializer):
        with transaction.atomic():
            site = serializer.save()
            group = Group.objects.get(name="Site Supervisor")
            UserRole.objects.get_or_create(user=self.request.user, site_id=site.id,
                                           project__id=site.project.id, group=group)
            noti = site.logs.create(source=self.request.user, type=11, title="new Site",
                                       organization=site.project.organization,
                                       project=site.project, site=site, content_object=site, extra_object=site.project,
                                       description='{0} created a new site named {1} in {2}'.format(self.request.user.get_full_name(),
                                                                                 site, site.project.name))
            result = {}
            result['description'] = noti.description
            result['url'] = noti.get_absolute_url()
            ChannelGroup("project-{}".format(site.project.id)).send({"text": json.dumps(result)})
            return site


class SiteUnderRegionViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = SiteSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteUnderProjectPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        if self.kwargs.get('region_pk') == "0":
            return queryset.filter(project_id = self.kwargs.get('pk'), region_id__isnull=True)
        return queryset.filter(project_id = self.kwargs.get('pk'), region_id=self.kwargs.get('region_pk'))

    def get_serializer_context(self):
        return {'request': self.request}

class SiteUnderProjectViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = SiteSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteUnderProjectPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(project__id=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}

class SiteUnderOrgViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = SiteSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteUnderProjectPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(project__organization_id=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}


class SiteReviewViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_survey=True)
    serializer_class = SiteReviewSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (SiteSurveyPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def filter_queryset(self, queryset):
        return queryset.filter(project__id=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}


class SiteReviewUpdateViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteReviewSerializer
    permission_classes = (SiteSurveyUpdatePermission,)

    def filter_queryset(self, queryset):
        return queryset.filter(pk=self.kwargs.get('pk', None))

    def get_serializer_context(self):
        return {'request': self.request}


class ProjectTypeViewset(viewsets.ModelViewSet):
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = (ProjectViewPermission,)
    parser_classes = (MultiPartParser, FormParser,)

    def get_serializer_context(self):
        return {'request': self.request}

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20

class SitePagignatedViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = MinimalSiteSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)

class SiteSearchViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Region.
    """
    queryset = Site.objects.filter(is_survey=False)
    serializer_class = MinimalSiteSerializer

    def filter_queryset(self, queryset):
        project_id = self.kwargs.get('pk', None)
        return queryset.filter(project__id=project_id)

    def get_queryset(self):
        query = self.request.REQUEST.get("q")
        return self.queryset.filter(name__icontains=query)


def all_notification(user,  message):
    ChannelGroup("%s" % user).send({
        "text": json.dumps({
            "msg": message
        })
    })

