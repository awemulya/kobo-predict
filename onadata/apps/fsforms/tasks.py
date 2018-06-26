from celery import task
from django.db import transaction

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FieldSightXF, Schedule


@task()
def copy_schedule_to_sites(schedule, fxf_status, pk):
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


@task()
def copy_to_sites(fxf):
    with transaction.atomic():
        for site in fxf.project.sites.filter(is_active=True):
            child, created = FieldSightXF.objects.get_or_create(is_staged=False, is_scheduled=False,
                                                                default_submission_status=fxf.default_submission_status,
                                                                xf=fxf.xf, site=site, fsform=fxf)
            child.is_deployed = True
            child.save()
            print(child.id)