from django.db import transaction
from django.core.management.base import BaseCommand

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FieldSightXF, FInstance
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


class Command(BaseCommand):
    help = 'Deploy Stages'

    def handle(self, *args, **options):
        count = 0
        issue = 0
        to_remove = 0
        to_create = 0
        affected_responses = 0
        projects  = Project.objects.all()
        for project in projects:
            for form in project.project_forms.all():
                count += 1
                sub_count = form.project_form_instances.all().count()
                mongo_count = settings.MONGO_DB.instances.find({'fs_project_uuid': str(form.id)}).count()
                if sub_count != mongo_count:
                    issue += 1
                    difference = (sub_count - mongo_count)
                    if difference < 0 :
                        to_remove += abs(difference)
                    else:
                        to_create += abs(difference)
                    affected_responses += abs(difference)
                    print str(count) + "   Actual count : " + str(sub_count) + "; Mongo Count : " + str(mongo_count) + " --- " + form.xf.title  + " / " + project.name + " / " + project.organization.name
            
        print "Form issue count : " + str(issue)
        print "Total affected_responses : " + str(affected_responses)
        print "Form to be removed from mongo : " +str(to_remove)
        print "Form to be created in mongo : " +str(to_create)
       




# for x in fi:
#     d = x.instance.parsed_instance.to_dict_for_mongo()
#     d.update({'fs_project_uuid': str(x.project_fxf_id), 'fs_project': x.project_id, 'fs_status': 0, 'fs_site':x.site_id, 'fs_uuid':x.site_fxf_id})
#     update_mongo_instance(d)