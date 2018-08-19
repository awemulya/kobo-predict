from celery import task
from django.db import transaction

from onadata.apps.fieldsight.models import Site, Project
from onadata.apps.fsforms.models import FieldSightXF, Schedule, Stage, DeployEvent
from onadata.apps.fsforms.serializers.ConfigureStagesSerializer import StageSerializer
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormListSerializer, StageFormSerializer
from onadata.apps.fsforms.utils import send_sub_stage_deployed_project, send_bulk_message_stage_deployed_project, \
    send_bulk_message_stages_deployed_project


@task(max_retries=10)
def copy_allstages_to_sites(pk):
    try:
        project = Project.objects.get(pk=pk)
        sites = project.sites.filter(is_active=True)
        main_stages = project.stages.filter(stage__isnull=True)
        main_stages_list = [ms for ms in main_stages]
        if not main_stages_list:
            return True
        with transaction.atomic():

            FieldSightXF.objects.filter(is_staged=True, site__project=project, stage__isnull=False). \
                update(stage=None, is_deployed=False, is_deleted=True)
            FieldSightXF.objects.filter(is_staged=True, project=project, is_deleted=False).update(is_deployed=True)
            Stage.objects.filter(site__project=project).delete()
            for main_stage in main_stages:
                for site in sites:
                    site_main_stage = Stage(name=main_stage.name, order=main_stage.order, site=site,
                                            description=main_stage.description, project_stage_id=main_stage.id)
                    site_main_stage.save()
                    project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk, stage_forms__is_deleted=False)
                    for project_sub_stage in project_sub_stages:
                        if project_sub_stage.tags and site.type:
                            if not site.type.id in project_sub_stage.tags:
                                continue
                        site_sub_stage = Stage(name=project_sub_stage.name, order=project_sub_stage.order, site=site,
                                               description=project_sub_stage.description,
                                               stage=site_main_stage, weight=project_sub_stage.weight,
                                               project_stage_id=project_sub_stage.id)
                        site_sub_stage.save()
                        if FieldSightXF.objects.filter(stage=project_sub_stage).exists():
                            fsxf = FieldSightXF.objects.filter(stage=project_sub_stage)[0]
                            site_fsxf, created = FieldSightXF.objects.get_or_create(is_staged=True,
                                                                                    xf=fsxf.xf, site=site,
                                                                                    fsform=fsxf, stage=site_sub_stage)
                            site_fsxf.is_deleted = False
                            site_fsxf.is_deployed = True
                            site_fsxf.default_submission_status = fsxf.default_submission_status
                            site_fsxf.save()
        send_bulk_message_stages_deployed_project(project)
    except Exception as e:
        num_retries = copy_allstages_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_allstages_to_sites.retry(countdown=seconds_to_wait)


@task(max_retries=10)
def copy_stage_to_sites(main_stage, pk):
    try:
        project = Project.objects.get(pk=pk)
        sites = project.sites.filter(is_active=True)
        project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk, stage_forms__is_deleted=False)
        sub_stages_id = [s.id for s in project_sub_stages]
        project_forms = FieldSightXF.objects.filter(stage__id__in=sub_stages_id, is_deleted=False)
        project_form_ids = [p.id for p in project_forms]
        with transaction.atomic():
            FieldSightXF.objects.filter(pk__in=project_form_ids).update(is_deployed=True)  # deploy this stage

            FieldSightXF.objects.filter(fsform__id__in=project_form_ids).update(stage=None, is_deployed=False,
                                                                                is_deleted=True)
            deleted_forms = FieldSightXF.objects.filter(fsform__id__in=project_form_ids)
            deleted_stages_id = sub_stages_id
            if main_stage.id:
                deleted_stages_id.append(main_stage.id)
            deleted_stages = Stage.objects.filter(project_stage_id__in=deleted_stages_id)
            Stage.objects.filter(project_stage_id=main_stage.id).delete()
            Stage.objects.filter(project_stage_id__in=sub_stages_id).delete()
            sites_affected = []
            for site in sites:
                site_data = {'id': site.id}
                site_main_stage = Stage(name=main_stage.name, order=main_stage.order, site=site,
                                        description=main_stage.description, project_stage_id=main_stage.id)
                site_main_stage.save()
                site_data['main_stage'] = StageSerializer(site_main_stage).data
                site_data['sub_stage_data'] = []
                for project_sub_stage in project_sub_stages:
                    if project_sub_stage.tags and site.type:
                        if site.type.id not in project_sub_stage.tags:
                            continue
                    sub_stage_data = {}
                    site_sub_stage = Stage(name=project_sub_stage.name, order=project_sub_stage.order, site=site,
                                           description=project_sub_stage.description, stage=site_main_stage,
                                           project_stage_id=project_sub_stage.id, weight=site_main_stage.weight)
                    site_sub_stage.save()
                    if FieldSightXF.objects.filter(stage=project_sub_stage).exists():
                        fsxf = FieldSightXF.objects.filter(stage=project_sub_stage)[0]
                        site_fsxf, created = FieldSightXF.objects.get_or_create(is_staged=True,
                                                                                xf=fsxf.xf, site=site,
                                                                                fsform=fsxf, stage=site_sub_stage)
                        site_fsxf.is_deleted = False
                        site_fsxf.is_deployed = True
                        site_fsxf.default_submission_status = fsxf.default_submission_status
                        site_fsxf.save()
                        sub_stage_data['sub_stage'] = StageSerializer(site_sub_stage).data
                        sub_stage_data['sub_stage_form'] = StageFormSerializer(site_fsxf).data
                        site_data['sub_stage_data'].append(sub_stage_data)
                sites_affected.append(site_data)

            deploy_data = {
                'project_stage': StageSerializer(main_stage).data,
                'project_sub_stages': StageSerializer(project_sub_stages, many=True).data,
                'project_forms': StageFormSerializer(project_forms, many=True).data,
                'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
                'deleted_stages': StageSerializer(deleted_stages, many=True).data,
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

@task(max_retries=10)
def copy_sub_stage_to_sites(sub_stage, pk):
    try:
        project = Project.objects.get(pk=pk)
        sites = project.sites.filter(is_active=True)
        site_ids = []
        main_stage = sub_stage.stage
        stage_form = sub_stage.stage_forms

        with transaction.atomic():
            FieldSightXF.objects.filter(pk=stage_form.pk).update(is_deployed=True)
            stage_form.is_deployed = True
            stage_form.save()

            FieldSightXF.objects.filter(fsform__id=stage_form.id).update(stage=None, is_deployed=False, is_deleted=True)

            deleted_forms = FieldSightXF.objects.filter(fsform__id=stage_form.id)
            deleted_stages = Stage.objects.filter(project_stage_id=sub_stage.id, stage__isnull=False)

            Stage.objects.filter(project_stage_id=sub_stage.id, stage__isnull=False).delete()
            sites_affected = []
            for site in sites:
                if sub_stage.tags and site.type:
                    if not site.type.id in sub_stage.tags:
                        continue
                site_data = {}
                try:
                    site_main_stage = Stage.objects.get(project_stage_id=main_stage.id, site=site)
                    site_main_stage.name = main_stage.name
                    site_main_stage.order = main_stage.order
                    site_main_stage.description = main_stage.description
                    site_main_stage.save()
                    site_data['main_stage'] = StageSerializer(site_main_stage).data
                    site_data['site'] = site.id
                except Exception as e:
                    site_main_stage = Stage(name=main_stage.name, order=main_stage.order, site=site,
                                            description=main_stage.description, project_stage_id=main_stage.id)
                    site_main_stage.save()
                    site_data['main_stage'] = StageSerializer(site_main_stage).data
                    site_data['site'] = site.id

                site_sub_stage = Stage(name=sub_stage.name, order=sub_stage.order, site=site,
                                       description=sub_stage.description, project_stage_id=sub_stage.id,
                                       stage=site_main_stage, weight=sub_stage.weight)
                site_sub_stage.save()
                site_fsxf, created = FieldSightXF.objects.get_or_create(
                    is_staged=True,
                    xf=stage_form.xf, site=site, fsform=stage_form, stage=site_sub_stage)
                site_fsxf.is_deleted = False
                site_fsxf.is_deployed = True
                site_fsxf.default_submission_status = stage_form.default_submission_status
                site_fsxf.save()
                site_data['sub_stage'] = StageSerializer(site_sub_stage).data
                site_data['main_stage'] = StageSerializer(site_main_stage).data
                site_data['sub_stage_form'] = StageFormSerializer(site_fsxf).data
                site_data['id'] = site.id
                sites_affected.append(site_data)
            deploy_data = {'project_forms': [StageFormSerializer(stage_form).data],
                       'project_stage': StageSerializer(main_stage).data,
                       'project_sub_stages': [StageSerializer(sub_stage).data],
                       'deleted_forms': StageFormSerializer(deleted_forms, many=True).data,
                       'deleted_stages': StageSerializer(deleted_stages, many=True).data,
                       'sites_affected': sites_affected,
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

@task(max_retries=10)
def copy_schedule_to_sites(schedule, fxf_status, pk):
    try:
        fxf = schedule.schedule_forms
        selected_days = tuple(schedule.selected_days.all())
        with transaction.atomic():
            if not fxf_status:
                # deployed case
                fxf.is_deployed = True
                fxf.save()
                FieldSightXF.objects.filter(fsform=fxf, is_scheduled=True, site__project__id=pk).update(is_deployed=True,
                                                                                                        is_deleted=False)
                for site in Site.objects.filter(project__id=pk, is_active=True):
                    _schedule, created = Schedule.objects.get_or_create(name=schedule.name, site=site)
                    if created:
                        _schedule.selected_days.add(*selected_days)
                        child = FieldSightXF(is_scheduled=True, default_submission_status=fxf.default_submission_status,
                                             xf=fxf.xf, site=site, fsform=fxf,
                                             schedule=_schedule, is_deployed=True)
                        child.save()

            else:
                # undeploy
                fxf.is_deployed = False
                fxf.save()
                FieldSightXF.objects.filter(fsform=fxf, is_scheduled=True, site__project_id=pk).update(is_deployed=False,
                                                                                                       is_deleted=True)
    except Exception as e:
        print(str(e))
        num_retries = copy_schedule_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_schedule_to_sites.retry(countdown=seconds_to_wait)


@task(max_retries=10)
def copy_to_sites(fxf):
    try:
        with transaction.atomic():
            for site in fxf.project.sites.filter(is_active=True):
                child, created = FieldSightXF.objects.get_or_create(is_staged=False, is_scheduled=False, xf=fxf.xf, site=site, fsform=fxf)
                child.is_deployed = True
                child.default_submission_status = fxf.default_submission_status
                child.save()
    except Exception as e:
        print(str(e))
        num_retries = copy_to_sites.request.retries
        seconds_to_wait = 2.0 ** num_retries
        # First countdown will be 1.0, then 2.0, 4.0, etc.
        raise copy_to_sites.retry(countdown=seconds_to_wait)
