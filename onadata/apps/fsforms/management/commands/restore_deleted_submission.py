from django.core.management.base import BaseCommand
from django.conf import settings

from onadata.apps.fsforms.models import FInstance
from onadata.apps.logger.models import Instance


class Command(BaseCommand):
    help = 'Restore deleted submission'

    def add_arguments(self, parser):
        parser.add_argument('-l', '--submission_id', nargs='+', help=' python manage.py restore_deleted_submission  -l '
                                                                     '<submission_id1> <submission_id2> <submission_id3 '
                                                                     '<....submission_idn>', required=True)

    def handle(self, *args, **options):

        submission_id = options['submission_id']
        try:
            FInstance.deleted_objects.filter(instance_id__in=submission_id).update(is_deleted=False)
            Instance.objects.filter(id__in=submission_id).update(deleted_at=None)

            # Also update in mongo from mongo shell ' db.instances.update( {_id: {$in: <submission_id_lis>}},{$unset:{'_deleted_at':1}})'

            self.stdout.write('Successfully restore deleted submission "%s"' % submission_id)

        except Exception as e:
            print(str(e))
