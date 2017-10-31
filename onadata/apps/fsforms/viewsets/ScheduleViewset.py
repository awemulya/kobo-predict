import json

from rest_framework import viewsets
from rest_framework.response import Response

from onadata.apps.fsforms.models import Schedule, Days, FieldSightXF
from onadata.apps.fsforms.serializers.ScheduleSerializer import ScheduleSerializer, DaysSerializer
from channels import Group as ChannelGroup

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

    def get_serializer_context(self):
        return self.kwargs

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
            noti = fxf.logs.create(source=self.request.user, type=19, title="Schedule",
                                  organization=fxf.site.project.organization,
                                  project = fxf.site.project,
                                  site = fxf.site, content_object=fxf, extra_object = fxf.site,
                                              extra_message='{0} form {1}'.format(fxf.form_type(), fxf.xf.title),
                                  description='{0} assigned new Schedule form  {1} to {2} '.format(
                                      self.request.user.get_full_name(),
                                      fxf.xf.title,
                                      fxf.site.name
                                  ))
            result = {}
            result['description'] = noti.description
            result['url'] = noti.get_absolute_url()
            ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
            ChannelGroup("project-{}".format(fxf.site.project.id)).send({"text": json.dumps(result)})
        else:
            fxf.save()
            noti = fxf.logs.create(source=self.request.user, type=18, title="Schedule",
                      organization=fxf.project.organization,
                      project = fxf.project, content_object=fxf, extra_object=fxf.project, extra_message='{0} form {1}'.format(fxf.form_type(), fxf.xf.title),
                      description='{0} assigned new Schedule form  {1} to {2} '.format(
                          self.request.user.get_full_name(),
                          fxf.xf.title,
                          fxf.project.name
                      ))
            result = {}
            result['description'] = noti.description
            result['url'] = noti.get_absolute_url()
            # ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
            ChannelGroup("project-{}".format(fxf.project.id)).send({"text": json.dumps(result)})
        


class DayViewset(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing and editing scheduless.
    """
    queryset = Days.objects.all()
    serializer_class = DaysSerializer
