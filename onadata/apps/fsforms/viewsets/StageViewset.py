from rest_framework import viewsets

from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer


class StageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Form Groups.
    """
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
