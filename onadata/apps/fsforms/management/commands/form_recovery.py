from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances
from django.conf import settings
from onadata.apps.fsforms.models import FInstance
import json
class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        f=FInstance.objects.filter(project_fxf__is_staged=True, site_fxf=None, site=None).values_list('instance', flat=True)
        fm =list(settings.MONGO_DB.instances.find({ "_id": { "$in": list(f) } }, {"fs_site":1, "_id":1}))
        

        data_dict = {}
        
        for list_data in fm:
            data_dict[list_data['_id']] = list_data['fs_site']


        import pdb; pdb.set_trace()