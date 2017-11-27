import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from onadata.apps.fieldsight.models import TimeZone

class Command(BaseCommand):
    help = 'Create default groups'
    timezonesreader = csv.reader(open("onadata/apps/fieldsight/management/commands/timezones.csv"), delimiter=",")
    header = timezonesreader.next()  # header

    def handle(self, *args, **options):
        timezonesreader = csv.reader(open("onadata/apps/fieldsight/management/commands/timezones.csv"), delimiter=",")
        for country_code, country_name, time_zone, gmt_offset, in timezonesreader:

            timezone, created = TimeZone.objects.get_or_create(country_code=country_code,country=country_name,time_zone=time_zone,offset_time=gmt_offset)
            self.stdout.write('Successfully created Timestamp .. "%s"' % timezone)
