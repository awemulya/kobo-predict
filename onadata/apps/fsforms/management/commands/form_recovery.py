from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances
from django.conf import settings
from onadata.apps.fsforms.models import FInstance

class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        f=FInstance.objects.filter(project_fxf__is_staged=True, site_fxf=None, site=None).values_list('instance', flat=True)
        fm =settings.MONGO_DB.instances.find({ "_id": { "$in": [29387] } })
        import pdb; pdb.set_trace()