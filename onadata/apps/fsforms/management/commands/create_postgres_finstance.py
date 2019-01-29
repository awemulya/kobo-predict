import pandas as pd

from django.conf import settings

from onadata.apps.fieldsight.models import Project
from onadata.apps.fsforms.models import FInstance
from onadata.apps.logger.models import Instance

from django.core.management.base import BaseCommand


def validate_column_sequence(columns):
    return True


def create_finstance_from_mongo(submission_id_list, sheet_columns, project_id):

    submission_id, site_identifier = tuple(sheet_columns)
    submission_id_list = submission_id_list

    project = Project.objects.get(pk=project_id)

    site = project.sites.get(identifier=site_identifier)
    if FInstance.objects.filter(instance=submission_id).exists():
        print("Submission Id Exist  ", submission_id)
    else:
        print("creating Finstance for  ", submission_id, ".......")
        query = {"_id": {"$in": submission_id_list}}
        xform_instances = settings.MONGO_DB.instances
        cursor = xform_instances.find(query,  { "_id": 1, "fs_project_uuid":1, "fs_project":1 , "fs_site":1,'fs_uuid':1 })

        records = list(record for record in cursor)

        for record in records:
            instance = Instance.objects.get(pk=submission_id)
            fi = FInstance(instance=instance, site=site, project=site.project, project_fxf=record["fs_project_uuid"], form_status=0, submitted_by=instance.user)
            fi.set_version()
            fi.save()


def process(xl, to_transfer_sheet, project_id):
    df = xl.parse(to_transfer_sheet)
    submission_id_list = df['Submission Id'].tolist()
    columns = df.columns
    create_finstance_from_mongo(submission_id_list, columns, project_id)

    # if validate_column_sequence(columns):
    #     for i in range(len(df.values)):
    #         create_finstance_from_mongo(df.values[i], project_id)


class Command(BaseCommand):
    help = 'Create Finstance from mongo'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str)
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **options):
        file_path = options['file_path']
        project_id = options['project_id']
        self.stdout.write('Reading file "%s"' % file_path)
        xl = pd.ExcelFile(file_path)
        sheet = xl.sheet_names[0]
        process(xl, sheet, project_id)
        self.stdout.write('Reading file "%s"' % file_path)