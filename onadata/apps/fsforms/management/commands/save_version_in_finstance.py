from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import FInstance
from onadata.apps.logger.models import Instance
from onadata.settings.local_settings import XML_VERSION_MAX_ITER
import re


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
            n = XML_VERSION_MAX_ITER
            limit = offset + batchsize
            instances = FInstance.objects.filter(instance__xform__user__username=username, version='')[offset:limit]
            inst = list(instances)
            if instances:
                self.stdout.write("Updating instances from #{} to #{}\n".format(
                        inst[0].id,
                        inst[-1].id))
                
                for instance in instances:
                    i = Instance.objects.get(fieldsight_instance=instance)
                    xml = i.xml
                    
                    pattern = re.compile('version="(.*)">')
                    m = pattern.search(xml)
                    if m:
                        instance.version = m.group(1)
                        instance.save()
                        continue
                    
                    for i in range(n, 0, -1):
                        p = re.compile('<_version__00{0}>(.*)</_version__00{1}>'.format(i, i))
                        m = p.search(instance)
                        if m:
                            instance.version = m.group(1)
                            instance.save()
                            continue

                    p = re.compile('<_version_>(.*)</_version_>')
                    m = p.search(xml)
                    if m:
                        instance.version = m.group(1)
                        instance.save()
                        continue
                    
                    p1 = re.compile('<__version__>(.*)</__version__>')
                    m1 = p1.search(xml)
                    if m1:
                        instance.version = m.group(1)
                        instance.save()
                        continue                    
                    
            else:
                stop = True
                
            offset += batchsize