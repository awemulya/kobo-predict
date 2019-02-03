from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import FInstance


class Command(BaseCommand):
    help = 'Set version in FInstance for given user'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        # xls_directory = "/home/xls"
        batchsize = options.get("batchsize", 100)
        username = options['username']
        stop = False
        offset = 0
        while stop is not True:
            limit = offset + batchsize
            instances = FInstance.objects.filter(instance__xform__user__username=username)[offset:limit]
            inst = list(instances)
            if instances:
                self.stdout.write("Updating instances from #{} to #{}\n".format(
                        inst[0].id,
                        inst[-1].id))
                
                for instance in instances:
                    instance.save()

            else:
                stop = True
                
            offset += batchsize