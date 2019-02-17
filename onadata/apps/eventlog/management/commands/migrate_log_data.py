from django.core.management.base import BaseCommand
from onadata.apps.eventlog.models import *

class Command(BaseCommand):
    help = 'Migrate log data.'

    def add_arguments(self, parser):
        parser.add_argument('ids', type=str)

    def handle(self, *args, **options):
        ids = options['ids']
        _input = ids.split(',')
        if len(_input) > 2:
            return

        start = _input[0]
        end = _input[1]
        print start, end, "+++++++++++++++++++++++++++=="
        logs = FieldSightLog.objects.all()[start:end]

        for log in logs:
            log.save()

        self.stdout.write('Successfully completed.')


    
    extra_obj_name = models.CharField(max_length=255, blank=True)
    event_name = models.CharField(max_length=255, blank=True)



    # def save(self, *args, **kwargs):
    #     try:
    #         self.event_name = self.content_object.getname()
    #     except:
    #         self.event_name = ""
    #     try:
    #         if self.extra_object is None:
    #             self.extra_obj_name = ""

    #         elif self.extra_content_type.model == "user":
    #             if self.extra_object.user_profile:
    #                 self.extra_obj_name =  self.extra_object.user_profile.getname()
    #             else:
    #                 self.extra_obj_name =  self.extra_object.email
    #         elif:
    #             self.extra_obj_name =  self.extra_object.getname()
    #     except:
    #         self.extra_obj_name = ""
        
    #     super(FieldSightLog, self).save(*args, **kwargs)
    #     