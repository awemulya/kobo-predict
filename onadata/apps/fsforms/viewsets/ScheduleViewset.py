from rest_framework import viewsets

from onadata.apps.fsforms.models import Schedule, Days
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer, DaysSerializer


class ScheduleViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Schedule.objects.filter(fieldsightxf__isnull=False)
    serializer_class = ScheduleSerializer

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


class DayViewset(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Days.objects.all()
    serializer_class = DaysSerializer
