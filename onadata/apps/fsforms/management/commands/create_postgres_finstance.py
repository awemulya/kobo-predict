import pandas as pd

from django.conf import settings

from onadata.apps.fieldsight.models import Project
from onadata.apps.fsforms.models import FInstance
from onadata.apps.logger.models import Instance

from django.core.management.base import BaseCommand
from onadata.apps.viewer.models.parsed_instance import update_mongo_instance


def validate_column_sequence(columns):
    return True


def create_finstance_from_mongo(sheet_columns, project_id):

    submission_id, site_identifier = tuple(sheet_columns)
    project = Project.objects.get(pk=project_id)

    site = project.sites.get(identifier=site_identifier)

    if FInstance.objects.filter(instance=submission_id).exists():
        print("Submission Id Exist  ", submission_id)
    else:
        print("creating Finstance for  ", submission_id, ".......")
        # query = {"_id": {"$in": submission_id_list}}
        query = {"_id": submission_id}

        xform_instances = settings.MONGO_DB.instances
        cursor = xform_instances.find(query,  { "_id": 1, "fs_project_uuid":1, "fs_project":1 , "fs_site":1,'fs_uuid':1 })

        # records = list(record for record in cursor)
        record = list(cursor)

        instance = Instance.objects.get(pk=submission_id)
        fi = FInstance(instance=instance, site=site, project=site.project, project_fxf=record["fs_project_uuid"],
                       form_status=0, submitted_by=instance.user)
        fi.set_version()
        fi.save()
        instance = FInstance.objects.get(instance=instance)
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

        # records = list(record for record in cursor)
        #
        # for record in records:
        #     instance = Instance.objects.get(pk=submission_id)
        #     fi = FInstance(instance=instance, site=site, project=site.project, project_fxf=record["fs_project_uuid"], form_status=0, submitted_by=instance.user)
        #     fi.set_version()
        #     fi.save()
        #     # instance = FInstance.objects.get(instance=instance)
        #     # d = instance.instance.parsed_instance.to_dict_for_mongo()
        #     # d.update(
        #     #     {'fs_project_uuid': str(instance.project_fxf_id), 'fs_project': instance.project_id, 'fs_status': 0,
        #     #      'fs_site': instance.site_id,
        #     #      'fs_uuid': instance.site_fxf_id})
        #     # try:
        #     #     synced = update_mongo_instance(d, instance.id)
        #     #     print(synced, "updated in mongo success")
        #     # except Exception as e:
        #     #     print(str(e))


def process(xl, to_transfer_sheet, project_id):
    df = xl.parse(to_transfer_sheet)
    submission_id_list = df['Submission Id'].tolist()
    columns = df.columns
    # create_finstance_from_mongo(submission_id_list, columns, project_id)

    if validate_column_sequence(columns):
        for i in range(len(df.values)):
            create_finstance_from_mongo(df.values[i], project_id)


class Command(BaseCommand):
    help = 'Create Finstance from mongo if site does not exist'

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