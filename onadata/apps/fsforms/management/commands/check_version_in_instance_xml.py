from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import FInstance
from onadata.settings.local_settings import XML_VERSION_MAX_ITER

import os
import re

class Command(BaseCommand):
    help = 'Check if version exists in instance xml'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('batchsize', type=int)

    def handle(self, *args, **options):
        n = XML_VERSION_MAX_ITER

        batchsize = options.get("batchsize", 50)
        username = options['username']
        stop = False
        offset = 0

        while stop is not True:
            limit = offset + batchsize
            instances = FInstance.objects.filter(instance__xform__user__username=username)[offset:limit]
            inst = list(instances)

            if instances:
                self.stdout.write("Checking version in instances from #{} to #{}\n".format(
                        inst[0].id,
                        inst[-1].id))
                for instance in instances:
                    xml = instance.instance.xml

                    pattern = re.compile('version="(.*)">')
                    m = pattern.search(xml)
                    if m:
                        continue
                    
                    for i in range(6, 0, -1):
                        p = re.compile('<_version__00{0}>(.*)</_version__00{1}>'.format(i, i))
                        m = p.search(instance)
                        if m:
                            continue

                    p = re.compile('<_version_>(.*)</_version_>')
                    m = p.search(xml)
                    if m:
                        continue
                    
                    p1 = re.compile('<__version__>(.*)</__version__>')
                    m1 = p1.search(xml)
                    if m1:
                        continue

                    print('No version in instance xml of instance id:', instance.instance.id)

            else:
                stop = True
                
            offset += batchsize


