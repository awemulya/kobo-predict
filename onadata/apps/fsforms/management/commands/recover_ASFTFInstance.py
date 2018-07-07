from django.core.management.base import BaseCommand, CommandError
from onadata.apps.fsforms.models import FInstance, FieldSightXF
import json
class Command(BaseCommand):
    #ASFTFInstance.py
    help = 'Recovery for FInstances of FSForms of type `general`, `scheduled` and `stage` with site and site level form but without site form ids in site_fxf.'
    def handle(self, *args, **options):
        siteforms = FInstance.objects.all(site__isnull=False, site_fxf__isnull=True)
        print "Total sites to be recovered = " + str(siteforms.count())
        for respo in siteforms:
            if respo.project_fxf:
                site_form = FieldSightXF.objects.filter(fsform_id=respo.project_fxf_id, site_id=respo.site_id)
                if site_form:
                    respo.site_fxf = site_form[0].id
                    respo.save()
                    print ">>>>>Sucess, fixed for instance = " + str(respo.instance_id)
                else:
                    print "-----Error, No site level form exists for project_form id = " + str(respo.project_fxf) 
            else:
                print "------Error, No project levelform for instance_id = " + str(respo.instance_id)
                continue 
        print ""
        print ""
        print "--------------End of Code--------------"       
