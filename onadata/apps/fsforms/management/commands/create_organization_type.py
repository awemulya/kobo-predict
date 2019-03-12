from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import OrganizationType


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        org_type_list = ['Academic', 'Local Nonprofit/NGO',
                         'International Nonprofit/NGO', 'Private Company',
                         'Local Government',
                         'Sub-National (State/Provincial) Government',
                         'National Government',
                         'Bilateral Government Donor',
                         'Multilateral Institution',
                         'International Financial Institution', 'Other']
        for org_type in org_type_list:
            OrganizationType.objects.get_or_create(name=org_type)
            self.stdout.write('Successfully created Organization Type .. "%s"' % org_type)