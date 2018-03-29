from rest_framework import viewsets
from rest_framework.response import Response
import rest_framework.status

from onadata.apps.fsforms.models import Stage, EducationMaterial
from onadata.apps.fsforms.serializers.ConfigureStagesSerializer import StageSerializer, SubStageSerializer, \
    SubStageDetailSerializer, EMSerializer


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

    def retrieve_by_id(self, request, *args, **kwargs):
        instance = Stage.objects.get(pk=kwargs.get('pk'))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = Stage.objects.get(pk=kwargs.get('pk'))
        name = self.request.data.get('name', False)
        if not name:
            return Response({'error':'No Stage Name Provided'}, status=status.HTTP_400_BAD_REQUEST)
        desc = self.request.data.get('description', "")
        instance.name = name
        instance.description = desc
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

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
    A simple ViewSet for viewing and editing Sub Stages.
    """
    queryset = Stage.objects.all().order_by('order')
    serializer_class = SubStageDetailSerializer

    # def filter_queryset(self, queryset):
    #     if self.request.user.is_anonymous():
    #         self.permission_denied(self.request)
    #     stage_id = self.kwargs.get('stage_id', None)
    #     queryset = queryset.filter(stage__id=stage_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request, 'kwargs': self.kwargs,}


class EmViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing em of Stages.
    """
    queryset = EducationMaterial.objects.all()
    serializer_class = EMSerializer

    def retrieve_by_id(self, request, *args, **kwargs):
        stage = Stage.objects.get(pk=kwargs.get('pk'))
        try:
            instance = stage.em
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except:
            return Response({})

    # def update(self, request, *args, **kwargs):
    #     instance = Stage.objects.get(pk=kwargs.get('pk'))
    #     name = self.request.data.get('name', False)
    #     if not name:
    #         return Response({'error':'No Stage Name Provided'}, status=status.HTTP_400_BAD_REQUEST)
    #     desc = self.request.data.get('description', "")
    #     instance.name = name
    #     instance.description = desc
    #     instance.save()
    #     serializer = self.get_serializer(instance)
    #     return Response(serializer.data)

    def get_serializer_context(self):
        return {'request': self.request, 'kwargs': self.kwargs,}
