from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import XformHistory
from onadata.settings.local_settings import XML_VERSION_MAX_ITER

import os
import re

class Command(BaseCommand):
    help = 'Check if version exists in XformHistory xml'


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
            xformhistory = XformHistory.objects.filter(xform__user__username=username)[offset:limit]
            xf_hist = list(xformhistory)
            if xformhistory:
                self.stdout.write("Checking version in Xformhistory from #{} to #{}\n".format(
                        xf_hist[0].id,
                        xf_hist[-1].id))

                for item in xformhistory:            
                    xml = item.xml
                    pattern = re.compile('version="(.*)">')
                    m = pattern.search(xml)
                    if m:
                        continue

                    #second priority version labels
                    #_version__006 has more priority than _verison__005
                    for i in range(6, 0, -1):
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
                        print('found')
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

                    print('No versions found in xformhistory', item.id_string)
            else:
                stop = True
                
            offset += batchsize