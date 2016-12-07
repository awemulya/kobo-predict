from rest_framework import viewsets

from onadata.apps.fsforms.models import Schedule, Days
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer, DaysSerializer


class ScheduleViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Schedule.objects.filter(fieldsightxf__isnull=True)
    serializer_class = ScheduleSerializer


class DayViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Days.objects.all()
    serializer_class = DaysSerializer
