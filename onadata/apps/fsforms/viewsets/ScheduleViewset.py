from rest_framework import viewsets

from onadata.apps.fsforms.models import Stage, Schedule
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer


class ScheduleViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Schedule.objects.filter()
    serializer_class = ScheduleSerializer
