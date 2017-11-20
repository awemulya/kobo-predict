from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import Timezone

TIME_ZONE = {
    # 0 : 'Monday',
    # 1 : 'Tuesday',
    # 2 : 'Wednesday',
    # 3 : 'Thursday',
    # 4 : 'Friday',
    # 5 : 'Saturday',
    # 6 : 'Sunday',
}


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):

        for index, time in TIME_ZONE.items():
            _, created = Timezone.objects.get_or_create(index=index, timezone=timezone)
            self.stdout.write('Successfully created Timezones .. "%s"' % timezone)