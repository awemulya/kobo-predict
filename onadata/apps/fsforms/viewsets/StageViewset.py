from __future__ import unicode_literals

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import Stage, FInstance
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer, SubStageSerializer, StageSerializer1
from rest_framework.pagination import PageNumberPagination

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 5

class StageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True, stage__isnull=True)
    serializer_class = StageSerializer1
    # pagination_class = LargeResultsSetPagination

    # authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)


    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        is_project = self.kwargs.get('is_project', None)
        pk = self.kwargs.get('pk', None)
        if is_project == "1":
            queryset = queryset.filter(project__id=pk)
        else:
            project_id = get_object_or_404(Site, pk=pk).project.id
            queryset = queryset.filter(Q(site__id=pk, project_stage_id=0) | Q(project__id=project_id))
        return queryset

    def get_serializer_context(self):
        instances = []
        is_project = self.kwargs.get("is_project")
        pk = self.kwargs.get("pk")
        if is_project == "1":
            instances = FInstance.objects.filter(project__isnull=False,
                                                 project__id=pk,
                                                 project_fxf__is_staged=True,
                                                 ).order_by('-pk').select_related("project", "project_fxf")
        if is_project == "0":
            instances = FInstance.objects.filter(site__id=pk).order_by('-pk').select_related("site", "site_fxf")
        self.kwargs.update({'instances': instances})
        return {'request': self.request, 'kwargs': self.kwargs,'instances': instances}


class MainStageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and Main Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True, stage__isnull=True)
    serializer_class = StageSerializer


class SiteMainStageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and site Main Stages.
    """
    queryset = Stage.objects.all()
    serializer_class = StageSerializer

    def filter_queryset(self, queryset):
        site_id = self.kwargs.get('site_id', None)
        site_id = int(site_id)
        queryset = queryset.filter(stage_forms__isnull=True, stage__isnull=True,site__id=site_id)
        return queryset


class SubStageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and site Main Stages.
    """
    queryset = Stage.objects.all()
    serializer_class = SubStageSerializer

    def filter_queryset(self, queryset):
        main_stage = self.kwargs.get('main_stage', None)
        main_stage = int(main_stage)
        queryset = queryset.filter(stage__id=main_stage)
        return queryset
