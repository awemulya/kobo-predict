from django.db import transaction
from django.core.management.base import BaseCommand

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FieldSightXF, FInstance
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


class Command(BaseCommand):
    help = 'Deploy Stages'

    def handle(self, *args, **options):
        organization_id = 13
        # project_id = 30
        sites = Site.objects.filter(project__organization__id=organization_id).values_list('id', flat=True)
        for site_id in sites:
            # self.stdout.write('Operating in site '+str(site_id))
            with transaction.atomic():
                finstances = FInstance.objects.filter(site_id=site_id, site_fxf_id__isnull=False)
                for fi in finstances:
                    site_fsxf = fi.site_fxf
                    if site_fsxf.site.id != site_id:
                        correct_form = FieldSightXF.objects.get(site__id=site_id, is_staged=True, fsform=fi.project_fxf, is_deleted=False)
                        fi.site_fxf = correct_form
                        fi.save()
                        parsed_instance = fi.instance.parsed_instance
                        d = parsed_instance.to_dict_for_mongo()
                        d.update({'fs_uuid': correct_form.id})
                        update_mongo_instance(d)
                        self.stdout.write('Successfully corrected form')
