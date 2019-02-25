from django.core.management.base import BaseCommand
from onadata.apps.logger.models import XForm
from onadata.apps.fsforms.models import XformHistory
from onadata.settings.local_settings import XML_VERSION_MAX_ITER

import os
import re

class Command(BaseCommand):
    help = 'Check if xformhistory with matching version with xform exists'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        n = XML_VERSION_MAX_ITER
        username = options['username']
        
        xform = XForm.objects.filter(user__username=username)
        xf= list(xform)
        version = ''

        if xform:
            for item in xform:

                #check for version in tag<(id) id="" version="">
                xml = item.xml
                pattern = re.compile('version="(.*)">')
                m = pattern.search(xml)
                if m:
                    version = m.group(1)

                else:
                    #second priority version labels
                    #_version__006 has more priority than _verison__005
                    for i in range(n, 0, -1):
                        #for old version labels(containing both letters and alphabets)
                        p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version__00{0}" """.format(i))
                        m = p.search(xml)
                        if m:
                            version = m.group(1)

                        else:                            
                            #for old version labels(containing only numbers)
                            p = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version__00{0}" """.format(i))
                            m1 = p.search(xml)
                            if m1:
                                version = m1.group(1)
                    
                    if not version:
                        #next priority version label
                        #for old version labels
                        p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version_" """)
                        m = p.search(xml)
                        if m:
                            version = m.group(1)
                        
                        else:
                            #for old version labels
                            p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version_" """)
                            m1 = p.search(xml)
                            if m1:
                                version = m1.group(1)
                            else:
                                #next priority version label
                                #for new version labels
                                p1 = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/__version__" """)
                                m1 = p1.search(xml)
                                if m1:
                                    version = m1.group(1)
                                else:
                                    #for new version labels
                                    p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/__version__" """)
                                    m1 = p1.search(xml)
                                    if m1:
                                        version = m1.group(1)

                xform_history = XformHistory.objects.filter(xform=item)

                for hist in xform_history:
                    if version == hist.version:
                        print('Deleting xformhistory with id: ', hist.id)
                        hist.delete()
                    else:
                        continue