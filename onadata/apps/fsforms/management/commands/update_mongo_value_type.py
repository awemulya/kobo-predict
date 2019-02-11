from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = "Update value type of fs_site and fs_uuid in mongo instances to make string type to int type"

    def handle(self, *args, **kwargs):
        xform_instances = settings.MONGO_DB.instances
        
        #type 2 is for string type
        query = {'$and':[{'fs_site':{'$type':2}}, {'fs_uuid':{'$type':2}}]}
        
        cursor = xform_instances.find(query)
        for record in cursor:
            fs_site = record['fs_site']
            if fs_site == '':
                new_fs_site = None
            else:
                new_fs_site = int(fs_site)
            fs_uuid = record['fs_uuid']
            if fs_uuid == '':
                new_fs_uuid = None
            elif fs_uuid == 'None':
                new_fs_uuid = None
            else:
                new_fs_uuid = int(fs_uuid)
            xform_instances.update({'_id':record['_id']},{'$set':{'fs_site':new_fs_site, 'fs_uuid':new_fs_uuid}})
            print('Updating mongo instance for ' + str(record['_id']))
        print('Mongo instances updated.......')
