from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import ProjectType


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        _list = ['School', 'Clinic', 'Hospital', 'Government',
                         'Building', 'Road', 'Other Infrastructure', 'House', 'Water Supply System']
        for _type in _list:
            new, created = ProjectType.objects.get_or_create(name=_type)
            if created:
                self.stdout.write('Successfully created Project Type .. "%s"' % _type)
            else:
                self.stdout.write('Project Type  Already Exists.. "%s"' % _type)