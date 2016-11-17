from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import Days

DAY_OF_THE_WEEK = {
    0 : 'Monday',
    1 : 'Tuesday',
    2 : 'Wednesday',
    3 : 'Thursday',
    4 : 'Friday',
    5 : 'Saturday',
    6 : 'Sunday',
}


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):

        for index, day in DAY_OF_THE_WEEK.items():
            _, created = Days.objects.get_or_create(index=index, day=day)
            self.stdout.write('Successfully created Day .. "%s"' % day)