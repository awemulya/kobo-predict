from django.core.management.base import BaseCommand
from onadata.apps.logger.models import XForm
from onadata.settings.local_settings import XML_VERSION_MAX_ITER

import os
import re

class Command(BaseCommand):
    help = 'Check if version exists in xform xml'

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
            xform = XForm.objects.filter(user__username=username)[offset:limit]
            xf= list(xform)

            if xform:
                self.stdout.write("Checking version in xform from #{} to #{}\n".format(
                        xf[0].id,
                        xf[-1].id))
                for item in xform:

                    #check for version in tag<(id) id="" version="">
                    xml = item.xml
                    pattern = re.compile('version="(.*)">')
                    m = pattern.search(xml)
                    if m:
                        continue

                    #second priority version labels
                    #_version__006 has more priority than _verison__005
                    for i in range(n, 0, -1):
                        #for old version labels(containing both letters and alphabets)
                        p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version__00{0}" """.format(i))
                        m = p.search(xml)
                        if m:
                            continue
                        
                        #for old version labels(containing only numbers)
                        p = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version__00{0}" """.format(i))
                        m1 = p.search(xml)
                        if m1:
                            continue
                    
                    #next priority version label
                    #for old version labels
                    p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version_" """)
                    m = p.search(xml)
                    if m:
                        continue
                    
                    #for old version labels
                    p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version_" """)
                    m1 = p.search(xml)
                    if m1:
                        continue
                    
                    #next priority version label
                    #for new version labels
                    p1 = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/__version__" """)
                    m1 = p1.search(xml)
                    if m1:
                        continue
                    
                    #for new version labels
                    p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/__version__" """)
                    m1 = p1.search(xml)
                    if m1:
                        continue

                    print('No versions found in xform', item.id_string)
            else:
                stop = True
            offset += batchsize
