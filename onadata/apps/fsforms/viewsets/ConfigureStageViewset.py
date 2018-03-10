from rest_framework import viewsets
from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.ConfigureStagesSerializer import StageSerializer, SubStageSerializer, \
    SubStageDetailSerializer


class StageListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Main Stages.
    """
    queryset = Stage.objects.filter(stage_forms__isnull=True, stage__isnull=True).order_by('order')
    serializer_class = StageSerializer

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
        return {'request': self.request, 'kwargs': self.kwargs,}


class SubStageListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Main Stages.
    """
    queryset = Stage.objects.filter(stage__isnull=False).order_by('order')
    serializer_class = SubStageSerializer

    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        stage_id = self.kwargs.get('stage_id', None)
        queryset = queryset.filter(stage__id=stage_id)
        return queryset

    def get_serializer_context(self):
        return {'request': self.request, 'kwargs': self.kwargs,}


class SubStageDetailViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Main Stages.
    """
    queryset = Stage.objects.filter(stage__isnull=False).order_by('order')
    serializer_class = SubStageDetailSerializer

    # def filter_queryset(self, queryset):
    #     if self.request.user.is_anonymous():
    #         self.permission_denied(self.request)
    #     stage_id = self.kwargs.get('stage_id', None)
    #     queryset = queryset.filter(stage__id=stage_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request, 'kwargs': self.kwargs,}

