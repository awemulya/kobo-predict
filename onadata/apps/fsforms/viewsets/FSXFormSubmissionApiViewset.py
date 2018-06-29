from __future__ import unicode_literals
import json
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from onadata.apps.api.viewsets.xform_submission_api import XFormSubmissionApi
from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FieldSightXF, Stage, Schedule
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

        fsxfid = kwargs.get('pk', None)
        siteid = kwargs.get('site_id', None)
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
                                       project=instance.fieldsight_instance.site.project,
                                                        site=instance.fieldsight_instance.site,
                                                        extra_object=instance.fieldsight_instance.site,
                                                        content_object=instance.fieldsight_instance)
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


class ProjectFSXFormSubmissionApi(XFormSubmissionApi):
    serializer_class = FieldSightSubmissionSerializer
    template_name = 'fsforms/submission.xml'

    def create(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)

        fsxfid = kwargs.get('pk', None)
        siteid = kwargs.get('site_id', None)
        if siteid == '0':
            siteid = None
        if fsxfid is None:
            return self.error_response("Fieldsight Form ID Not Given", False, request)
        try:
            fs_proj_xf = get_object_or_404(FieldSightXF, pk=kwargs.get('pk'))
            fxf = None
            xform  = None
            try:
                if fs_proj_xf.is_survey:
                    xform = fs_proj_xf.xf
                elif fs_proj_xf.is_scheduled and siteid:
                    site = Site.objects.get(pk=siteid)
                    schedule = fs_proj_xf.schedule
                    selected_days = tuple(schedule.selected_days.all())
                    s, created = Schedule.objects.get_or_create(name=schedule.name, site=site, date_range_start=schedule.date_range_start,
                                                date_range_end=schedule.date_range_end)
                    if created:
                        s.selected_days.add(*selected_days)
                        s.save()
                    fxf, created = FieldSightXF.objects.get_or_create(is_scheduled=True, site=site,
                                                                      xf=fs_proj_xf.xf, from_project=True,
                                                                      fsform=fs_proj_xf, schedule=s)
                    xform = fxf.xf
                elif (fs_proj_xf.is_scheduled is False and fs_proj_xf.is_staged is False) and siteid:
                    site = Site.objects.get(pk=siteid)
                    fxf, created = FieldSightXF.objects.get_or_create(is_scheduled=False,is_staged=False, site=site,
                                                   xf=fs_proj_xf.xf, from_project=True, fsform=fs_proj_xf)
                    xform = fxf.xf
                elif fs_proj_xf.is_staged and siteid:
                    site = Site.objects.get(pk=siteid)
                    project_stage = fs_proj_xf.stage
                    try:
                        site_stage = Stage.objects.get(site=site, project_stage_id=project_stage.id)
                        fxf = site_stage.stage_forms
                        xform = fxf.xf
                    except Exception as e:
                        # return self.error_response("This Stage form not deployed in this site. Please Contact Administrators", False, request)
                        try:
                            with transaction.atomic():
                                project = fs_proj_xf.project
                                project_main_stages = project.stages.filter(stage__isnull=True)
                                for pms in project_main_stages:
                                    project_sub_stages = Stage.objects.filter(stage__id=pms.pk, stage_forms__is_deleted=False)
                                    site_main_stage, created = Stage.objects.get_or_create(name=pms.name, order=pms.order,
                                                                                           site=site,
                                                                                           description=pms.description,
                                                                                           project_stage_id=pms.id)
                                    for pss in project_sub_stages:
                                        if pss.tags and site.type:
                                            if not site.type.id in pss.tags:
                                                continue
                                        site_sub_stage, created = Stage.objects.get_or_create(name=pss.name, order=pss.order, site=site,
                                                       description=pss.description, stage=site_main_stage, project_stage_id=pss.id, weight=pss.weight)
                                        if FieldSightXF.objects.filter(stage=pss).exists():
                                            project_fsxf = pss.stage_forms
                                            site_form, created = FieldSightXF.objects.get_or_create(is_staged=True, xf=project_fsxf.xf,
                                                                                                    site=siteid,fsform=project_fsxf,
                                                                                                    stage=site_sub_stage,
                                                                                                    is_deployed=True)
                                            if project_fsxf.id == fs_proj_xf.id:
                                                fxf = site_form
                                                xform = fxf.xf
                        except Exception as e:
                            return self.error_response("Error Occured in submission {0}".format(str(e)), False, request)
                        if not (xform and fxf):
                            return self.error_response("This Stage form not deployed in this site. Please Contact Administrators", False, request)
            except Exception as e:
                xform = fs_proj_xf.xf
            proj_id = fs_proj_xf.project.id

        except:
            return self.error_response("Site Id Or Form ID Not Vaild", False, request)

        if request.method.upper() == 'HEAD':
            return Response(status=status.HTTP_204_NO_CONTENT,
                            headers=self.get_openrosa_headers(request),
                            template_name=self.template_name)
        site_fsxf_id = None
        if fxf:
            site_fsxf_id = fxf.id
        if fs_proj_xf.is_survey:
            error, instance = create_instance_from_xml(request, None, None, fs_proj_xf.id, proj_id, xform)
        else:
            error, instance = create_instance_from_xml(request, site_fsxf_id, siteid, fs_proj_xf.id, proj_id, xform)

        
        if error or not instance:
            return self.error_response(error, False, request)

        if fs_proj_xf.is_survey:
            noti = instance.fieldsight_instance.logs.create(source=self.request.user, type=16, title="new Project level Submission",
                                       organization=fs_proj_xf.project.organization,
                                       project=fs_proj_xf.project,
                                                        extra_object=fs_proj_xf.project,
                                                        extra_message="project",
                                                        content_object=instance.fieldsight_instance)
        else:
            site=Site.objects.get(pk=siteid)
            noti = instance.fieldsight_instance.logs.create(source=self.request.user, type=16, title="new Site level Submission",
                                       organization=fs_proj_xf.project.organization,
                                       project=fs_proj_xf.project, site=site,
                                                        extra_object=site,
                                                        content_object=instance.fieldsight_instance)
        result = {}
        result['description'] = noti.description
        result['url'] = noti.get_absolute_url()
        # ChannelGroup("notify-{}".format(self.object.project.organization.id)).send({"text": json.dumps(result)})
        # ChannelGroup("project-{}".format(self.object.project.id)).send({"text": json.dumps(result)})
        if instance.fieldsight_instance.site:
            ChannelGroup("site-{}".format(instance.fieldsight_instance.site.id)).send({"text": json.dumps(result)})
        else:
            ChannelGroup("project-{}".format(instance.fieldsight_instance.project.id)).send({"text": json.dumps(result)})

        # modify create instance

        

        context = self.get_serializer_context()
        serializer = FieldSightSubmissionSerializer(instance, context=context)
        return Response(serializer.data,
                        headers=self.get_openrosa_headers(request),
                        status=status.HTTP_201_CREATED,
                        template_name=self.template_name)



