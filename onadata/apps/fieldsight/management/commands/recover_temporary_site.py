from django.conf import settings
from django.core.management.base import BaseCommand
import pandas as pd

from onadata.apps.fieldsight.models import Project
from onadata.apps.fsforms.models import FInstance
from onadata.apps.logger.models import Instance
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


def validate_column_sequence(columns):
    return True


def move_submission(sheet_columns, project_id):
    sn, site_name, submission_id, site_id = tuple(sheet_columns)
    print(submission_id,  site_id)
    project = Project.objects.get(pk=project_id)

    to_site = project.sites.get(pk=site_id)
    if FInstance.objects.filter(instance=submission_id).exists():
        instance = FInstance.objects.get(instance=submission_id)
        instance.site = to_site
        instance.save()
        d = instance.instance.parsed_instance.to_dict_for_mongo()
        d.update(
            {'fs_project_uuid': str(instance.project_fxf_id), 'fs_project': instance.project_id, 'fs_status': 0,
             'fs_site': instance.site_id,
             'fs_uuid': instance.site_fxf_id})
        try:
            synced = update_mongo_instance(d, instance.id)
            print(synced, "updated in mongo success")
        except Exception as e:
            print(str(e))
    else:
        print("submision ", submission_id, "doesnot exists")


def process_recover_submissions(xl, to_transfer_sheet, project_id):
    df = xl.parse(to_transfer_sheet)
    columns = df.columns
    if validate_column_sequence(columns):
        for i in range(len(df.values)):
            move_submission(df.values[i], project_id)


class Command(BaseCommand):
    help = 'Create default groups'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **options):
        file_path = options['file_path']
        project_id = options['project_id']
        self.stdout.write('Reading file "%s"' % file_path)
        xl = pd.ExcelFile(file_path)
        recoverr_sheet = xl.sheet_names[0]
        process_recover_submissions(xl, recoverr_sheet, project_id)
        self.stdout.write('Reading file "%s"' % file_path)