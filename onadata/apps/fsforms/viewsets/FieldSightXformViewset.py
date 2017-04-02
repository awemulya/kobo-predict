from rest_framework import viewsets

from onadata.apps.fsforms.models import Stage, FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormSerializer
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer


class FieldSightXFormViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Fieldsight Xform.
    """
    queryset = FieldSightXF.objects.all()
    serializer_class = FSXFormSerializer


class GeneralFormsViewSet(viewsets.ModelViewSet):
    """
    General Forms
    """
    queryset = FieldSightXF.objects.filter(is_staged=False, is_scheduled=False)
    serializer_class = FSXFormSerializer

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

    def perform_create(self, serializer):
        fxf = serializer.save()
        fxf.is_deployed = True
        fxf.save()
