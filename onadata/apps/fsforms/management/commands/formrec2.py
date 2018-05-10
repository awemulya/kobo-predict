from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances
from django.conf import settings
from onadata.apps.fsforms.models import FInstance, FieldSightParsedInstance
from onadata.apps.viewer.models import ParsedInstance
import json
class Command(BaseCommand):
    help = 'Create default groups'
    

    def handle(self, *args, **options):
        ids =[ 21265, 21267, 21268, 21269, 21270, 21271, 21272, 21273, 21274,
            21275,
            21276,
            21277,
            21278,
            21279,
            21280,
            21282,
            21286,
            21287,
            21288,
            21289,
            21290,
            21291,
            21292,
            21293,
            21294,
            21295,
            21296,
            21297,
            21298,
            21299,
            21300,
            21301,
            21302,
            21303,
            21304,
            21305,
            21306,
            21307,
            21308,
            21309,
            21310,
            21311,
            21312,
            21313,
            21314,
            21316,
            21317,
            21318,
            21319,
            21320,
            21321,
            21322,
            21323,
            21324,
            21325,
            21326,
            21327,
            21328,
            21329,
            21330 ]
        # f=FInstance.objects.filter(date__range=["2018-4-10","2018-5-10"]).values_list('instance', flat=True)
        # fm =list(settings.MONGO_DB.instances.find({ "_id": { "$in": list(f) } }, {"_id":1}))
        # data = [id['_id'] for id in fm]

        # data2 =[item for item in f if item not in data ]
        # fm2 =list(settings.MONGO_DB.instances.find({ "_id": { "$in": list(data2) } }, {"_submission_time":1}))
        nf=FInstance.objects.filter(instance_id__in=ids)
        nnf = ParsedInstance.objects.filter(instance_id__in=ids)
        change_ids ={}

        # nnff = ParsedInstance.objects.get(instance_id=21319)
        # nnff.update_mongo(False)


        for fi in nf:
            
            if fi.site is None:
                site_id = ""
            else:
                site_id =fi.site_id

            if fi.project_fxf is None:
                project_fxf_id = ""
            else:
                project_fxf_id=fi.project_fxf_id

            if fi.project is None:
                project_id = ""
            else:
                project_id = fi.project_id

            if fi.site_fxf is None:
                site_fxf_id = ""
            else:
                site_fxf_id = fi.site_fxf_id

            main_data[fi.instance_id] = {'fs_uuid': site_fxf_id, 'fs_status': 0,'fs_site':site_id, 'fs_project':project_id,
            'fs_project_uuid':project_fxf_id}

        for finnf in nnf:
            if finnf.instance_id in main_data:
                finnf.save(update_fs_data=main_data.get(finnf.instance_id), async=False)
                finnf.to_dict_for_mongo()
        #     print created
        #     print pi
        #     if not created:
        #         pi.save(async=False)
        
            # for list_data in fm:
        #     data_dict[list_data['_id']] = int(list_data['fs_site'])

        # finstances=FInstance.objects.filter(project_fxf__is_staged=True, site_fxf=None, site=None)
        # count = 0
        # for k,v in data_dict.items():
        #     fi = FInstance.objects.get(instance_id=k)
        #     print fi.instance_id
            
                

        #     print count
        #     settings.MONGO_DB.instances.update({ "_id": k }, { "$set": { "fs_uuid": fi.site_fxf_id } })
               
        import pdb; pdb.set_trace()