import json

from rest_framework import viewsets

from onadata.apps.fsforms.models import Stage, FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormSerializer
from onadata.apps.fsforms.serializers.StageSerializer import StageSerializer
from onadata.apps.fsforms.utils import send_message
from channels import Group as ChannelGroup

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
        org = None
        if fxf.project:
            org = fxf.project.organization
            for site in fxf.project.sites.filter(is_active=True):
                child, created = FieldSightXF.objects.get_or_create(is_staged=False, is_scheduled=False, xf=fxf.xf, site=site, fsform=fxf)
                child.is_deployed = True
                child.save()
            noti = fxf.logs.create(source=self.request.user, type=18, title="General",
                                              organization=org,
                                              project = fxf.project,
                                              description='{0} assigned new General form  {1} to {2} '.format(
                                                  self.request.user.get_full_name(),
                                                  fxf.site_fxf.xf.title,
                                                  fxf.project.name
                                              ))
            result = {}
            result['description'] = noti.description
            result['url'] = noti.get_absolute_url()
            ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
            ChannelGroup("project-{}".format(fxf.project.id)).send({"text": json.dumps(result)})
        else:
            org = fxf.site.project.organization

            noti = fxf.logs.create(source=self.request.user, type=19, title="General",
                                              organization=org,
                                              site = fxf.site,
                                              description='{0} assigned new General form  {1} to {2} '.format(
                                                  self.request.user.get_full_name(),
                                                  fxf.site_fxf.xf.title,
                                                  fxf.site.name
                                              ))
            result = {}
            result['description'] = noti.description
            result['url'] = noti.get_absolute_url()
            ChannelGroup("site-{}".format(fxf.site.id)).send({"text": json.dumps(result)})
            ChannelGroup("project-{}".format(fxf.site.project.id)).send({"text": json.dumps(result)})
