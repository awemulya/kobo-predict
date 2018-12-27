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
    submission_id, from_site_identifier, to_site_identifier, form_name = tuple(sheet_columns)
    project = Project.objects.get(pk=project_id)

    to_site = project.sites.get(identifier=to_site_identifier)
    print(to_site.identifier)
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
            synced = update_mongo_instance(d)
            print(synced, "updated in mongo success")
        except Exception as e:
            print(str(e))
    else:
        print("submision ", submission_id, "doesnot exists")
        print("creating Finstance for  ", submission_id, ".......")
        query = {"_id": {"$in": submission_id}}
        xform_instances = settings.MONGO_DB.instances
        cursor = xform_instances.find(query,  { "_id": 1, "fs_project_uuid":1, "fs_project":1 , "fs_site":1,'fs_uuid':1 })
        records = list(record for record in cursor)
        for record in records:
            instance = Instance.objects.get(pk=submission_id)
            fi = FInstance(instance=instance, site=to_site, project=to_site.project, project_fxf=record["fs_project_uuid"], form_status=0, submitted_by=instance.user)
            fi.set_version()
            fi.save()




def process_transfer_submissions(xl, to_transfer_sheet, project_id):
    df = xl.parse(to_transfer_sheet)
    columns = df.columns
    if validate_column_sequence(columns):
        for i in range(len(df.values)):
            move_submission(df.values[i], project_id)


def process_delete_submission(xl, to_delete_sheet):
    df = xl.parse(to_delete_sheet)
    submission_ids = []
    for i in range(len(df.values)):
        submission_ids.append(df.values[i][0])
    result = FInstance.objects.filter(instance__id__in=submission_ids).update(is_deleted=True)
    print(result)


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
        to_transfer_sheet = xl.sheet_names[0]
        to_delete_sheet = xl.sheet_names[1]
        process_transfer_submissions(xl, to_transfer_sheet, project_id)
        process_delete_submission(xl, to_delete_sheet)
        self.stdout.write('Reading file "%s"' % file_path)