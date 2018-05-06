from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.db import transaction

from onadata.apps.fieldsight.models import Project
from onadata.apps.fsforms.models import FieldSightXF, Stage


class Command(BaseCommand):
    help = 'Deploy Stages'

    def handle(self, *args, **options):
            pk =  137
            project = Project.objects.get(pk=pk)
            sites = project.sites.filter(is_active=True)
            [s for s in sites]
            main_stages = project.stages.filter(stage__isnull=True)
            with transaction.atomic():
                for main_stage in main_stages:
                    for site in sites:
                        print(site.id, main_stage.order)
                        try:
                            site_main_stage = Stage.objects.get(project_stage_id=main_stage.id, site=site)
                            site_main_stage.name = main_stage.name
                            site_main_stage.order = main_stage.order
                            site_main_stage.description = main_stage.description
                        except Exception as e:
                            site_main_stage = Stage(name=main_stage.name, order=main_stage.order, site=site,
                                           description=main_stage.description, project_stage_id=main_stage.id)
                        site_main_stage.save()
                        project_sub_stages = Stage.objects.filter(stage__id=main_stage.pk, stage_forms__is_deleted=False)
                        for project_sub_stage in project_sub_stages:
                            try:
                                site_sub_stage = Stage.objects.get(project_stage_id=project_sub_stage.id, site=site)
                                site_sub_stage.name = project_sub_stage.name
                                site_sub_stage.order = project_sub_stage.order
                                site_sub_stage.description = project_sub_stage.description
                                site_sub_stage.weight = project_sub_stage.weight
                                site_sub_stage.save()
                                try:
                                    sub_stage_form = site_sub_stage.stage_forms
                                    sub_stage_form.is_deleted =False
                                    sub_stage_form.is_deployed =True
                                    sub_stage_form.save()
                                except Exception as e:
                                    print("sub stage but no form")
                                    if FieldSightXF.objects.filter(stage=project_sub_stage).exists():
                                        fsxf = FieldSightXF.objects.filter(stage=project_sub_stage)[0]
                                        site_fsxf, created = FieldSightXF.objects.get_or_create(is_staged=True, default_submission_status=fsxf.default_submission_status, xf=fsxf.xf, site=site,
                                                                           fsform=fsxf, stage=site_sub_stage)
                                        site_fsxf.is_deleted = False
                                        site_fsxf.is_deployed = True
                                        site_fsxf.save()
                                    else:
                                        print("no  form in project sub stage")

                            except Exception as e:
                                # import ipdb
                                # ipdb.set_trace()
                                site_sub_stage = Stage(name=project_sub_stage.name, order=project_sub_stage.order, site=site,
                                           description=project_sub_stage.description, stage=site_main_stage, project_stage_id=project_sub_stage.id, weight=project_sub_stage.weight)
                                site_sub_stage.save()
                                if FieldSightXF.objects.filter(stage=project_sub_stage).exists():
                                    fsxf = FieldSightXF.objects.filter(stage=project_sub_stage)[0]
                                    site_fsxf, created = FieldSightXF.objects.get_or_create(is_staged=True, default_submission_status=fsxf.default_submission_status, xf=fsxf.xf, site=site,
                                                                       fsform=fsxf, stage=site_sub_stage)
                                    site_fsxf.is_deleted = False
                                    site_fsxf.is_deployed = True
                                    site_fsxf.save()
            self.stdout.write('Successfully deployed')