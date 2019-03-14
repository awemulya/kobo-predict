from __future__ import absolute_import

from celery import shared_task
from django.contrib.auth.models import User

from django.db import transaction
from django.conf import settings

from onadata.apps.fieldsight.models import Site, Project
from onadata.apps.fsforms.models import FieldSightXF, Schedule, Stage, DeployEvent, XformHistory
from onadata.apps.fsforms.serializers.ConfigureStagesSerializer import StageSerializer
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormListSerializer, StageFormSerializer
from onadata.apps.fsforms.utils import send_sub_stage_deployed_project, send_bulk_message_stage_deployed_project, \
    send_bulk_message_stages_deployed_project, send_message_un_deploy_project, send_message_koboform_updated
from onadata.apps.logger.models import XForm
from onadata.libs.utils.fieldsight_tools import clone_kpi_form


@shared_task(max_retries=10, soft_time_limit=4200)
def copy_allstages_to_sites(pk):
    try:
        project = Project.objects.get(pk=pk)
        with transaction.atomic():
            FieldSightXF.objects.filter(is_staged=True, project=project, is_deleted=False).update(is_deployed=True)
        send_bulk_message_stages_deployed_project(project)
    except Exception as e:
        num_retries = copy_allstages_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_allstages_to_sites.retry(countdown=seconds_to_wait)


@shared_task(max_retries=10, soft_time_limit=4200)
def copy_stage_to_sites(main_stage, pk):
    try:
        project = Project.objects.get(pk=pk)
        project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk, stage_forms__is_deleted=False)
        sub_stages_id = [s.id for s in project_sub_stages]
        project_forms = FieldSightXF.objects.filter(stage__id__in=sub_stages_id, is_deleted=False)
        project_form_ids = [p.id for p in project_forms]
        with transaction.atomic():
            FieldSightXF.objects.filter(pk__in=project_form_ids).update(is_deployed=True)  # deploy this project  stage substages all forms

            deleted_forms = FieldSightXF.objects.filter(is_deleted=True, is_staged=True, project=project)
            sites_affected = []
            deploy_data = {
                'project_stage': StageSerializer(main_stage).data,
                'project_sub_stages': StageSerializer(project_sub_stages, many=True).data,
                'project_forms': StageFormSerializer(project_forms, many=True).data,
                'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
                'deleted_stages': [],
                'sites_affected': sites_affected,
            }
            d = DeployEvent(project=project, data=deploy_data)
            d.save()
            send_bulk_message_stage_deployed_project(project, main_stage, d.id)
    except Exception as e:
        print(str(e))
        num_retries = copy_stage_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_stage_to_sites.retry(countdown=seconds_to_wait)

@shared_task(max_retries=10, soft_time_limit=4200)
def copy_sub_stage_to_sites(sub_stage, pk):
    try:
        project = Project.objects.get(pk=pk)
        main_stage = sub_stage.stage
        stage_form = sub_stage.stage_forms

        with transaction.atomic():
            stage_form.is_deployed = True
            stage_form.save()
            deleted_forms = FieldSightXF.objects.filter(project__id=pk, is_deleted=True, is_staged=True)


            deploy_data = {'project_forms': [StageFormSerializer(stage_form).data],
                       'project_stage': StageSerializer(main_stage).data,
                       'project_sub_stages': [StageSerializer(sub_stage).data],
                       'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
                       'deleted_stages': [],
                       'sites_affected': [],
                       }
        d = DeployEvent(project=project, data=deploy_data)
        d.save()
        send_sub_stage_deployed_project(project, sub_stage, d.id)
    except Exception as e:
        print(str(e))
        num_retries = copy_sub_stage_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_sub_stage_to_sites.retry(countdown=seconds_to_wait)

@shared_task(max_retries=10, soft_time_limit=3200)
def copy_schedule_to_sites(schedule, fxf_status, pk):
    try:
        fxf = schedule.schedule_forms
        with transaction.atomic():
            if not fxf_status:
                # deployed case
                fxf.is_deployed = True
                fxf.save()
            else:
                # undeploy
                fxf.is_deployed = False
                fxf.save()
            send_message_un_deploy_project(fxf)
    except Exception as e:
        print(str(e))
        num_retries = copy_schedule_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_schedule_to_sites.retry(countdown=seconds_to_wait)


@shared_task(max_retries=5)
def post_update_xform(xform_id, user):
    existing_xform = XForm.objects.get(pk=xform_id)
    user = User.objects.get(pk=user)
    xf = XformHistory(xform=existing_xform, xls=existing_xform.xls, json=existing_xform.json,
                      description=existing_xform.description, xml=existing_xform.xml,
                      id_string=existing_xform.id_string, title=existing_xform.title, uuid=existing_xform.uuid)
    xf.save()

    existing_xform.logs.create(source=user, type=20, title="Kobo form Updated",
                                description="update kobo form ")

    send_message_koboform_updated(existing_xform)


@shared_task(max_retries=5)
def clone_form(user, token, project):
    name = "Test Form"
    clone, id_string = clone_kpi_form(settings.KPI_DEFAULT_FORM1_STRING, token, name)
    if clone:
        xf = XForm.objects.get(id_string=id_string)
        fxf, created = FieldSightXF.objects.get_or_create(xf=xf, project=project)
    else:
        print("Can't create a form. Please contact the administrator.")


# @shared_task(max_retries=10)
# def copy_to_sites(fxf):
#     try:
#         with transaction.atomic():
#             for site in fxf.project.sites.filter(is_active=True):
#                 child, created = FieldSightXF.objects.get_or_create(is_staged=False, is_scheduled=False, xf=fxf.xf, site=site, fsform=fxf)
#                 child.is_deployed = True
#                 child.default_submission_status = fxf.default_submission_status
#                 child.save()
#     except Exception as e:
#         print(str(e))
#         num_retries = copy_to_sites.request.retries
#         seconds_to_wait = 2.0 ** num_retries
#         # First countdown will be 1.0, then 2.0, 4.0, etc.
#         raise copy_to_sites.retry(countdown=seconds_to_wait)

#
#
# from __future__ import absolute_import
#
# from celery import shared_task
#
# from django.db import transaction
#
# from onadata.apps.fieldsight.models import Site, Project
# from onadata.apps.fsforms.models import FieldSightXF, Schedule, Stage, DeployEvent
# from onadata.apps.fsforms.serializers.ConfigureStagesSerializer import StageSerializer
# from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormListSerializer, StageFormSerializer
# from onadata.apps.fsforms.utils import send_sub_stage_deployed_project, send_bulk_message_stage_deployed_project, \
#     send_bulk_message_stages_deployed_project
#
#
# @shared_task(max_retries=10)
# def copy_allstages_to_sites(pk):
#     try:
#         project = Project.objects.get(pk=pk)
#         main_stages = project.stages.filter(stage__isnull=True)
#         main_stages_list = [ms for ms in main_stages]
#         if not main_stages_list:
#             return True
#         with transaction.atomic():
#
#             FieldSightXF.objects.filter(is_staged=True, site__project=project, stage__isnull=False). \
#                 update(stage=None, is_deployed=False, is_deleted=True)
#             FieldSightXF.objects.filter(is_staged=True, project=project, is_deleted=False).update(is_deployed=True)
#             Stage.objects.filter(site__project=project, project_stage_id___isnull=False).delete()
#         send_bulk_message_stages_deployed_project(project)
#     except Exception as e:
#         num_retries = copy_allstages_to_sites.request.retries
#         seconds_to_wait = 2.0 ** num_retries
#         # First countdown will be 1.0, then 2.0, 4.0, etc.
#         raise copy_allstages_to_sites.retry(countdown=seconds_to_wait)
#
#
# @shared_task(max_retries=10)
# def copy_stage_to_sites(main_stage, pk):
#     try:
#         project = Project.objects.get(pk=pk)
#         project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk, stage_forms__is_deleted=False)
#         sub_stages_id = [s.id for s in project_sub_stages]
#         project_forms = FieldSightXF.objects.filter(stage__id__in=sub_stages_id, is_deleted=False)
#         project_form_ids = [p.id for p in project_forms]
#         with transaction.atomic():
#             FieldSightXF.objects.filter(pk__in=project_form_ids).update(is_deployed=True)  # deploy this stage
#
#             FieldSightXF.objects.filter(fsform__id__in=project_form_ids).update(stage=None, is_deployed=False,
#                                                                                 is_deleted=True)
#             deleted_forms = FieldSightXF.objects.filter(fsform__id__in=project_form_ids)
#             deleted_stages_id = sub_stages_id
#             if main_stage.id:
#                 deleted_stages_id.append(main_stage.id)
#             deleted_stages = Stage.objects.filter(project_stage_id__in=deleted_stages_id)
#             Stage.objects.filter(project_stage_id=main_stage.id).delete()
#             Stage.objects.filter(project_stage_id__in=sub_stages_id).delete()
#             sites_affected = []
#             deploy_data = {
#                 'project_stage': StageSerializer(main_stage).data,
#                 'project_sub_stages': StageSerializer(project_sub_stages, many=True).data,
#                 'project_forms': StageFormSerializer(project_forms, many=True).data,
#                 'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
#                 'deleted_stages': StageSerializer(deleted_stages, many=True).data,
#                 'sites_affected': sites_affected,
#             }
#             d = DeployEvent(project=project, data=deploy_data)
#             d.save()
#             send_bulk_message_stage_deployed_project(project, main_stage, d.id)
#     except Exception as e:
#         print(str(e))
#         num_retries = copy_stage_to_sites.request.retries
#         seconds_to_wait = 2.0 ** num_retries
#         # First countdown will be 1.0, then 2.0, 4.0, etc.
#         raise copy_stage_to_sites.retry(countdown=seconds_to_wait)
#
# @shared_task(max_retries=10)
# def copy_sub_stage_to_sites(sub_stage, pk):
#     try:
#         project = Project.objects.get(pk=pk)
#         sites = project.sites.filter(is_active=True)
#         site_ids = []
#         main_stage = sub_stage.stage
#         stage_form = sub_stage.stage_forms
#
#         with transaction.atomic():
#             FieldSightXF.objects.filter(pk=stage_form.pk).update(is_deployed=True)
#             stage_form.is_deployed = True
#             stage_form.save()
#
#             FieldSightXF.objects.filter(fsform__id=stage_form.id).update(stage=None, is_deployed=False, is_deleted=True)
#
#             deleted_forms = FieldSightXF.objects.filter(fsform__id=stage_form.id)
#             deleted_stages = Stage.objects.filter(project_stage_id=sub_stage.id, stage__isnull=False)
#
#             Stage.objects.filter(project_stage_id=sub_stage.id, stage__isnull=False).delete()
#             deploy_data = {'project_forms': [StageFormSerializer(stage_form).data],
#                        'project_stage': StageSerializer(main_stage).data,
#                        'project_sub_stages': [StageSerializer(sub_stage).data],
#                        'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
#                        'deleted_stages': StageSerializer(deleted_stages, many=True).data,
#                        'sites_affected': [],
#                        }
#         d = DeployEvent(project=project, data=deploy_data)
#         d.save()
#         send_sub_stage_deployed_project(project, sub_stage, d.id)
#     except Exception as e:
#         print(str(e))
#         num_retries = copy_sub_stage_to_sites.request.retries
#         seconds_to_wait = 2.0 ** num_retries
#         # First countdown will be 1.0, then 2.0, 4.0, etc.
#         raise copy_sub_stage_to_sites.retry(countdown=seconds_to_wait)
#
# @shared_task(max_retries=10)
# def copy_schedule_to_sites(schedule, fxf_status, pk):
#     try:
#         fxf = schedule.schedule_forms
#         selected_days = tuple(schedule.selected_days.all())
#         with transaction.atomic():
#             if not fxf_status:
#                 # deployed case
#                 fxf.is_deployed = True
#                 fxf.save()
#                 FieldSightXF.objects.filter(fsform=fxf, is_scheduled=True, site__project__id=pk).update(is_deployed=True,
#                                                                                                         is_deleted=False)
#
#             else:
#                 # undeploy
#                 fxf.is_deployed = False
#                 fxf.save()
#                 FieldSightXF.objects.filter(fsform=fxf, is_scheduled=True, site__project_id=pk).update(is_deployed=False,
#                                                                                                        is_deleted=True)
#     except Exception as e:
#         print(str(e))
#         num_retries = copy_schedule_to_sites.request.retries
#         seconds_to_wait = 2.0 ** num_retries
#         # First countdown will be 1.0, then 2.0, 4.0, etc.
#         raise copy_schedule_to_sites.retry(countdown=seconds_to_wait)
#
#

