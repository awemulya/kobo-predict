import pyexcel as p

from django.core.management.base import BaseCommand

from onadata.apps.fieldsight.models import Project
from onadata.apps.fsforms.models import Stage


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        self.stdout.write('Successfully created .. ')
        data = []
        ss_index = {}
        stages_rows = []
        head_row = ["Site ID", "Name", "Address", "Latitude", "longitude", "Status"]
        project = Project.objects.get(pk=1)
        stages = project.stages.filter(stage__isnull=True)
        for stage in stages:
            sub_stages = stage.parent.all()
            if len(sub_stages):
                head_row.append("Stage :"+stage.name)
                stages_rows.append("Stage :"+stage.name)

                for ss in sub_stages:
                    head_row.append("Sub Stage :"+ss.name)
                    ss_index.update({head_row.index("Sub Stage :"+ss.name): ss.id})
        data.append(head_row)
        total_cols = len(head_row) - 6 # for non stages
        for site in project.sites.filter(is_active=True, is_survey=False):
            site_row = [site.identifier, site.name, site.address, site.latitude, site.longitude, site.status]
            site_row.extend([None]*total_cols)
            for k, v in ss_index.items():
                if Stage.objects.filter(project_stage_id=v, site=site).count() == 1:
                    site_sub_stage = Stage.objects.get(project_stage_id=v, site=site)
                    site_row[k] = site_sub_stage.form_status
            data.append(site_row)

        p.save_as(array=data, dest_file_name="media/stage-report/{}_stage_data.xls".format(project.id))