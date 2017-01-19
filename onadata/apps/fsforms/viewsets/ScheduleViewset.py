from rest_framework import viewsets

from onadata.apps.fsforms.models import Schedule, Days
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer, DaysSerializer


class ScheduleViewset(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Schedule.objects.filter(fieldsightxf__isnull=False)
    serializer_class = ScheduleSerializer

    def filter_queryset(self, queryset):
        site_id = self.kwargs.get('site_id', None)
        site_id = int(site_id)
        queryset = queryset.filter(site__id=site_id)
        return queryset


class DayViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Days.objects.all()
    serializer_class = DaysSerializer
