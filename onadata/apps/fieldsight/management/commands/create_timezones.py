import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import Timezone

class Command(BaseCommand):
    help = 'Create default groups'
    timezonesreader = csv.reader(open("onadata/apps/fieldsight/management/commands/timezones.csv"), delimiter=",")
    header = timezonesreader.next()  # header

    def handle(self, *args, **options):
        timezonesreader = csv.reader(open("onadata/apps/fieldsight/management/commands/timezones.csv"), delimiter=",")
        for country_name, country_name, time_zone, gmt_offset, in timezonesreader:

            print country_name, country_name, time_zone, gmt_offset
            # timezones = ['Country Code', 'Country Name', 'Time Zone', 'GMT Offset']
            # if timezones:
            #     print timezones
                # created = Timezone.objects.get_or_create(timezones=timezones)
                # self.stdout.write('Successfully created timezones .. "%s"' % timezones)



