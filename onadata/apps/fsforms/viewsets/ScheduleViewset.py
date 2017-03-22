from rest_framework import viewsets
from rest_framework.response import Response

from onadata.apps.fsforms.models import Schedule, Days, FieldSightXF
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer, DaysSerializer


class ScheduleViewset(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Schedule.objects.filter(schedule_forms__isnull=False)
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

    def perform_create(self, serializer):
        # from rest_framework.exceptions import ValidationError

        data = self.request.data

        # if "form" not in data:
        #     raise ValidationError({
        #         "form": "No Form Selected ",
        #     })
        # if data.has_key('site'):
        #     if FieldSightXF.objects.filter(xf=data["form"], is_scheduled=True, site=data["site"]).exists():
        #         raise ValidationError({
        #             "form": "Form Already Used ",
        #         })
        #     if FieldSightXF.objects.filter(xf=data["form"],is_scheduled=True, project=data["project"]).exists():
        #         raise ValidationError({
        #             "form": "Form Already Used ",
        #         })

        schedule = serializer.save()


        fxf = FieldSightXF(xf_id=data["xf"], is_scheduled=True, schedule=schedule, site=schedule.site,
                                    project=schedule.project)
        if data.has_key("site"):
            fxf.is_deployed=True
        fxf.save()


class DayViewset(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Days.objects.all()
    serializer_class = DaysSerializer
