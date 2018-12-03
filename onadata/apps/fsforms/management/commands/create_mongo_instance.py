from django.core.management.base import BaseCommand
from onadata.apps.logger.models import Instance
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


class Command(BaseCommand):
    help = 'Create mongo missing data'

    def handle(self, *args, **options):
        instances = Instance.objects.filter(is_synced_with_mongo=False)
        for i in instances:
            d = i.parsed_instance.to_dict_for_mongo()
            try:
                x = i.fieldsight_instance
                d.update({'fs_project_uuid': str(x.project_fxf_id), 'fs_project': x.project_id, 'fs_status': 0, 'fs_site':x.site_id, 'fs_uuid':x.site_fxf_id})
                try:
                    synced = update_mongo_instance(d)
                    print(synced, "updated in mongo success")
                except Exception as e:
                    print(str(e))
            except Exception as e:
                print(str(e))