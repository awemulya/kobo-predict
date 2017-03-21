from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FInstance, FieldSightXF


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        cursor = settings.MONGO_DB.instances.find()
        instances = list(cursor)
        try:
            with transaction.atomic():
                for instance in instances:
                    id = instance.get("_id", False)
                    if not id: continue
                    fs_site = instance.get("fs_site", None)
                    fs_uuid = instance.get("fs_uuid", None)
                    if not fs_uuid: continue
                    if not fs_site: continue
                    fs_project = instance.get("fs_project", False)
                    if not fs_project:
                        fs_project = Site.objects.get(pk=fs_site).project.id
                    fs_project_uuid = instance.get("fs_project_uuid", None)
                    if FieldSightXF.objects.filter(id=fs_uuid).exists():
                        FInstance.objects.create(instance_id=id, site_id=fs_site, project_id=fs_project,
                                                 site_fxf_id=fs_uuid, project_fxf_id=fs_project_uuid)

        except Exception as e:
            # import ipdb
            # ipdb.set_trace()
            self.stdout.write(e.message)
        self.stdout.write('Successfully created fieldsight instances')
