from django.core.management.base import BaseCommand
from onadata.apps.logger.models import Instance
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance

OLD_INSTANCES = [107, 10, 11, 16, 64, 73, 81, 85, 109, 112,
                 99045, 6, 7, 34, 36, 39, 43, 47, 52, 55, 57, 62, 82, 87,
                 99, 100, 113, 115, 118, 2188, 2, 9, 21, 37, 42, 63, 66,
                 67, 72, 104, 105, 106, 117, 32788, 53712, 53713,
                 53714, 53715, 57105]

class Command(BaseCommand):
    help = 'Create mongo missing data'

    def handle(self, *args, **options):
        instances = Instance.objects.filter(is_synced_with_mongo=False).exclude(pk__in=OLD_INSTANCES)
        for i in instances:
            d = i.parsed_instance.to_dict_for_mongo()
            try:
                x = i.fieldsight_instance
                d.update({'fs_project_uuid': str(x.project_fxf_id), 'fs_project': x.project_id, 'fs_status': 0, 'fs_site':str(x.site_id), 'fs_uuid':str(x.site_fxf_id)})
                try:
                    synced = update_mongo_instance(d, i,id)
                    print(synced, "updated in mongo success")
                except Exception as e:
                    print(str(e))
            except Exception as e:
                print(str(e))