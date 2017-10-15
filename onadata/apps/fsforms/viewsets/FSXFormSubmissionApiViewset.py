import json

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from onadata.apps.api.viewsets.xform_submission_api import XFormSubmissionApi
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightSubmissionSerializer import FieldSightSubmissionSerializer
from ..fieldsight_logger_tools import safe_create_instance
from channels import Group as ChannelGroup
# 10,000,000 bytes
DEFAULT_CONTENT_LENGTH = getattr(settings, 'DEFAULT_CONTENT_LENGTH', 10000000)


def create_instance_from_xml(request, fsid, site, fs_proj_xf, proj_id, xform):
    xml_file_list = request.FILES.pop('xml_submission_file', [])
    xml_file = xml_file_list[0] if len(xml_file_list) else None
    media_files = request.FILES.values()
    return safe_create_instance(fsid, xml_file, media_files, None, request, site, fs_proj_xf, proj_id, xform)


class FSXFormSubmissionApi(XFormSubmissionApi):
    serializer_class = FieldSightSubmissionSerializer
    template_name = 'fsforms/submission.xml'

    def create(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)

        fsxfid = kwargs.get('pk',None)
        siteid = kwargs.get('site_id',None)
        if fsxfid is None or siteid is None:
            return self.error_response("Site Id Or Form ID Not Given", False, request)
        try:
            fsxfid = int(fsxfid)
            fxf = get_object_or_404(FieldSightXF, pk=kwargs.get('pk'))
            fs_proj_xf = fxf.fsform.pk if fxf.fsform else None
            proj_id = fxf.fsform.project.pk if fxf.fsform else fxf.site.project.pk
            xform = fxf.xf
            # site_id = fxf.site.pk if fxf.site else None
        except:
            return self.error_response("Site Id Or Form ID Not Vaild", False, request)

        if request.method.upper() == 'HEAD':
            return Response(status=status.HTTP_204_NO_CONTENT,
                            headers=self.get_openrosa_headers(request),
                            template_name=self.template_name)
        error, instance = create_instance_from_xml(request, fsxfid, siteid, fs_proj_xf, proj_id, xform)

        noti = instance.fieldsight_instance.logs.create(source=self.request.user, type=16, title="new Submission",
                                       organization=instance.fieldsight_instance.site.project.organization,
                                       project=instance.fieldsight_instance.site.project, site=instance.fieldsight_instance.site, extra_object=instance.fieldsight_instance.site, content_object=instance.fieldsight_instance,
                                       description='{0} submitted a response for {1} {2} in {3}'.format(
                                           self.request.user.get_full_name(),
                                           instance.fieldsight_instance.site_fxf.form_type(),
                                           instance.fieldsight_instance.site_fxf.xf.title,
                                           instance.fieldsight_instance.site.name,
                                       ))
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        ChannelGroup("site-{}".format(instance.fieldsight_instance.site.id)).send({"text": json.dumps(result)})

        # modify create instance

        if error or not instance:
            return self.error_response(error, False, request)

        context = self.get_serializer_context()
        serializer = FieldSightSubmissionSerializer(instance, context=context)
        return Response(serializer.data,
                        headers=self.get_openrosa_headers(request),
                        status=status.HTTP_201_CREATED,
                        template_name=self.template_name)



