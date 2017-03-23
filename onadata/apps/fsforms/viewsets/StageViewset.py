from rest_framework import viewsets

from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer, SubStageSerializer, AllStageSerializer, \
    AllSubStagesSerializer


class StageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True, stage__isnull=True)
    serializer_class = AllSubStagesSerializer


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
