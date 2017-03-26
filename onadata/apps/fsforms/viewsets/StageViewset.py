from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication

from onadata.apps.api.viewsets.xform_viewset import CsrfExemptSessionAuthentication
from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer, SubStageSerializer, StageSerializer1


class StageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True, stage__isnull=True)
    serializer_class = StageSerializer1

    # authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)

    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        is_project = self.kwargs.get('is_project', None)
        pk = self.kwargs.get('pk', None)
        if is_project == "1":
            queryset = queryset.filter(project__id=pk)
        else:
            queryset = queryset.filter(site__id=pk)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request}


class MainStageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and Main Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True,stage__isnull=True)
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
