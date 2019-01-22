from django.core.management.base import BaseCommand

from onadata.apps.logger.models import Instance
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


class Command(BaseCommand):
    help = 'Project submission form transfer'

    def add_arguments(self, parser):
        parser.add_argument('submission_id', type=int)
        parser.add_argument('transfer_to', type=int)

    def handle(self, *args, **options):
        submission_id = options['submission_id']
        transfer_to = options['transfer_to']

        instance = Instance.objects.get(id=submission_id)
        transfer_to = FieldSightXF.objects.get(id=transfer_to)
        valid_xf = transfer_to.xf
        instance.xform = valid_xf
        instance.save()

        d = instance.parsed_instance.to_dict_for_mongo()
        try:
            x = instance.fieldsight_instance
            d.update({'fs_project_uuid': str(x.project_fxf_id), 'fs_project': x.project_id, 'fs_status': 0,
                      'fs_site': x.site_id, 'fs_uuid': x.site_fxf_id})
            try:
                synced = update_mongo_instance(d, instance.id)
                print(synced, "updated in mongo success")
            except Exception as e:
                print(str(e))
        except Exception as e:
            print(str(e))
        self.stdout.write('Successfully transfer project submission form in "%s"' % transfer_to)
