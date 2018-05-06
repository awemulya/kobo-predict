from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances
from django.conf import settings
from onadata.apps.fsforms.models import FInstance
import json
class Command(BaseCommand):
    help = 'Create default groups'
# {27694: 58651, 27695: 58663, 27697: 58664, 27701: 58651, 29877: 23866, 29878: 23866, 29881: 23866, 29831: 23896, 29834: 23896, 29837: 23896, 29839: 23896, 29841: 23896, 29843: 23896, 29845: 23896, 29847: 23896, 29850: 23900, 29851: 23900, 29854: 23900, 29857: 23900, 29858: 23900, 29861: 23900, 29862: 23900, 29863: 23900, 29866: 23866, 29868: 23866, 29870: 23866, 29873: 23866, 29874: 23866, 29363: 26646, 29364: 26646, 29365: 26646, 29366: 26646, 29367: 26646, 29368: 26646, 29369: 26646, 29370: 26646, 29371: 26646, 29372: 26646, 29373: 26640, 29374: 26640, 29375: 26640, 29376: 26640, 29377: 26640, 29378: 26640, 29379: 26640, 29380: 26640, 29381: 26630, 29382: 26630, 29383: 26566, 29384: 26566, 29385: 26566, 29386: 26566, 29387: 26566, 29388: 26566, 29389: 26566, 29390: 26566, 29391: 26566, 28455: 24040, 28457: 24040, 28460: 24040, 28464: 24040, 28468: 24040, 28479: 24040, 28488: 24040, 28489: 24040, 28490: 24040, 28491: 24040, 28524: 23777, 28525: 23777, 28526: 23777, 28527: 23777, 28528: 23777, 28529: 23777, 28530: 23777, 28531: 24043, 28532: 24043, 28533: 24043, 28534: 24043, 28535: 24043, 28537: 24043, 28538: 24043, 28540: 24043, 28545: 23772, 28546: 23772, 28547: 23772, 28548: 23772, 28549: 23771, 28551: 23771, 28552: 23771, 28553: 23771, 28554: 23771, 28555: 23771, 28556: 23771, 28557: 23771, 28558: 24040, 28559: 24040, 28563: 23777, 12262: 9025}

    def handle(self, *args, **options):
        f=FInstance.objects.filter(project_fxf__is_staged=True, site_fxf=None, site=None).values_list('instance', flat=True)
        fm =list(settings.MONGO_DB.instances.find({ "_id": { "$in": list(f) } }, {"fs_site":1, "_id":1}))
        

        data_dict = {}
        
        for list_data in fm:
            data_dict[list_data['_id']] = int(list_data['fs_site'])

        finstances=FInstance.objects.filter(project_fxf__is_staged=True, site_fxf=None, site=None)
        count = 0
        for finstance in finstances:
            if finstance.instance_id in data_dict:
                count += 1
                site_id = data_dict[finstance.instance_id]
                site_fxf = finstance.project_fxf.parent.filter(pk=site_id)[0]
                print str(site_id) + ", " + str(finstance.instance_id)  +", "+ str(site_fxf.id)
                print count
        import pdb; pdb.set_trace()