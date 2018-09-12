from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.db import transaction

from onadata.apps.fsforms.models import Stage


class Command(BaseCommand):
    help = 'Move substage from one stage to another from project'

    def handle(self, *args, **options):
            self.stdout.write('Start .. .. ')
            with transaction.atomic():
                sub_stage_id = 1009214
                destination_stage_id = 1032402
                destination_main_stage = Stage.objects.get(pk=destination_stage_id)
                # update project stage of substage  to new destination
                Stage.objects.filter(pk=sub_stage_id).update(stage=destination_main_stage)
                site_sub_stages = Stage.objects.filter(project_stage_id=sub_stage_id)
                for ss in site_sub_stages:
                    site_destination_main_stage , created= Stage.objects.get_or_create(site=ss.site,name=destination_main_stage.name, description=destination_main_stage.description)
                    print("created", created)
                    site_destination_main_stage.order = destination_main_stage.order
                    site_destination_main_stage.project_stage_id = destination_main_stage.id
                    site_destination_main_stage.save()

                    ss.stage = site_destination_main_stage
                    ss.save()