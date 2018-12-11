from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Create default groups'

    def add_arguments(self, parser):
        parser.add_argument('instanceid', type=int)

    def handle(self, *args, **options):
        instanceid = options['instanceid']
        xform_instances = settings.MONGO_DB.instances
        instances_ids = [instanceid]
        query = {"_id": {"$in": instances_ids}}
        cursor = xform_instances.find(query)
        mongo_ids = list(record for record in cursor)
        print(mongo_ids)
        self.stdout.write('Reading instance "%s"' % str(instanceid))
