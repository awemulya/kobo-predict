from datetime import datetime
from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import TimeZone, Project, ProjectGeoJSON

from onadata.apps.fieldsight.models import Organization, Project, Site, Region, SiteType

from onadata.apps.fieldsight.fs_exports.formParserForExcelReport import parse_form_response
from io import BytesIO
from django.shortcuts import get_object_or_404
from onadata.apps.fsforms.models import FieldSightXF, FInstance, Stage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Prefetch

import os, tempfile, zipfile
from django.conf import settings
from django.core.files.storage import get_storage_class
from onadata.libs.utils.viewer_tools import get_path

import pyexcel as p
from .metaAttribsGenerator import get_form_answer, get_form_sub_status, get_form_submission_count, get_form_ques_ans_status
from django.conf import settings

class Command(BaseCommand):
    help = 'Create progress report for all projects with sites greater than 2000'
    
    def handle(self, *args, **options):
    	
def generate_stage_status_report():
	count = 0 
    projects = Project.objects.filter(active=True)
    for project in projects:
        if Site.objects.filter(project_id=project.id).count() < 2000:
            continue
        else: 

            try:
                data = []
                ss_index = {}
                stages_rows = []
                head_row = ["Site ID", "Name", "Region ID", "Latitude", "longitude", "Status"]
                
                stages = project.stages.filter(stage__isnull=True)
                for stage in stages:
                    sub_stages = stage.parent.all()
                    if len(sub_stages):
                        head_row.append("Stage :"+stage.name)
                        stages_rows.append("Stage :"+stage.name)

                        for ss in sub_stages:
                            head_row.append("Sub Stage :"+ss.name)
                            ss_index.update({head_row.index("Sub Stage :"+ss.name): ss.id})
                head_row.extend(["Site Visits", "Submission Count", "Flagged Submission", "Rejected Submission"])
                data.append(head_row)
                total_cols = len(head_row) - 6 # for non stages
                for site in project.sites.filter(is_active=True, is_survey=False):
                    flagged_count = 0 
                    rejected_count = 0
                    submission_count = 0

                    if site.region:
                        site_row = [site.identifier, site.name, site.region.identifier, site.latitude, site.longitude, site.site_status]
                    else:
                        site_row = [site.identifier, site.name, site.region_id, site.latitude, site.longitude, site.site_status]

                    site_row.extend([None]*total_cols)
                    for k, v in ss_index.items():
                        if Stage.objects.filter(id=v).count() == 1:
                            site_sub_stage = Stage.objects.get(id=v)
                            site_row[k] = site_sub_stage.site_submission_count(v, site.id)
                            submission_count += site_row[k]
                            flagged_count += site_sub_stage.flagged_submission_count(v, site.id)
                            rejected_count += site_sub_stage.rejected_submission_count(v, site.id)
                        else:
                            site_row[k] = 0



                    site_visits = settings.MONGO_DB.instances.aggregate([{"$match":{"fs_site": str(site.id)}},  { "$group" : { 
                          "_id" :  
                            { "$substr": [ "$start", 0, 10 ] }
                          
                       }
                     }])['result']

                    site_row[-1] = rejected_count
                    site_row[-2] = flagged_count
                    site_row[-3] = submission_count
                    site_row[-4] = len(site_visits) 

                    data.append(site_row)

                p.save_as(array=data, dest_file_name="media/stage-report/{}_stage_data.xls".format(project.id))
                xl_data = open("media/stage-report/{}_stage_data.xls".format(project.id), "rb")
                
                #Its only quick fix for now, save it in aws bucket whenever possible.

                project.progress_report = xl_data.name
                project.save()
                count += 1
                
            except Exception as e:
                print 'Report Gen Unsuccesfull. %s' % e
                print e.__dict__
        
        self.stdout.write('Created "%s " report for projects with success!' % (count))
        print datetime.now()