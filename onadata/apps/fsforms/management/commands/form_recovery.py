from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances

class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        import pdb; pdb.set_trace()