from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import OrganizationType


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        org_type_list = ['Government', 'Local NGO', 'INGO', 'Local Business', 'MultiNational']
        for org_type in org_type_list:
            new, created = OrganizationType.objects.get_or_create(name=org_type)
            self.stdout.write('Successfully created Organization Type .. "%s"' % org_type)