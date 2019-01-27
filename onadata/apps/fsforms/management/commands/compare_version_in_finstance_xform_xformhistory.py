from django.core.management.base import BaseCommand
from onadata.apps.logger.models import XForm, Instance
from onadata.apps.fsforms.models import XformHistory, FInstance
from onadata.settings.local_settings import XML_VERSION_MAX_ITER

import os
import re

class Command(BaseCommand):
    help = 'Check if XForm and XformHistory contains version of FInstance'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        n = XML_VERSION_MAX_ITER
        batchsize = options.get("batchsize", 50)
        username = options['username']
        stop = False
        offset = 0
        
        while stop is not True:
            limit = offset + batchsize
            finstances = FInstance.objects.filter(instance__xform__user__username=username)[offset:limit]
            inst = list(finstances)

            if finstances:
                self.stdout.write("Checking version in xform from #{} to #{}\n".format(
                        inst[0].id,
                        inst[-1].id))

                for finstance in finstances:
                    finstance_version = finstance.version

                    if finstance.project_fxf:
                        xml = finstance.project_fxf.xf.xml
                    else:
                        xml = finstance.site_fxf.xf.xml

                    # check for version in tag<(id) id="" version="">
                    pattern = re.compile('version="(.*)">')
                    m = pattern.search(xml)
                    if m:
                        xform_version = m.group(1)

                    else:
                        #second priority version labels
                        #_version__006 has more priority than _verison__005
                        for i in range(n, 0, -1):
                            #for old version labels(containing both letters and alphabets)
                            p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version__00{0}" """.format(i))
                            m = p.search(xml)
                            if m:
                                xform_version = m.group(1)
                                print('Version found')
                            
                            else:
                                #for old version labels(containing only numbers)
                                p = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version__00{0}" """.format(i))
                                m1 = p.search(xml)
                                if m1:
                                    xform_version = m1.group(1)
                        
                        if xform_version:
                            pass

                        else:
                            #next priority version label
                            #for old version labels
                            p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version_" """)
                            m = p.search(xml)
                            if m:
                                xform_version = m.group(1)
                            
                            else:
                                #for old version labels
                                p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/_version_" """)
                                m1 = p.search(xml)
                                if m1:
                                    xform_version = m1.group(1)

                                else:
                                    #next priority version label
                                    #for new version labels
                                    p1 = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/__version__" """)
                                    m1 = p1.search(xml)
                                    if m1:
                                        xform_version = m1.group(1)

                                    else:
                                        #for new version labels
                                        p1 = re.compile("""<bind calculate="(.*)" nodeset="/(.*)/__version__" """)
                                        m1 = p1.search(xml)
                                        if m1:
                                            xform_version = m1.group(1)

                    if finstance_version == xform_version:
                        continue
    
                    elif XformHistory.objects.filter(xform__user__username=username, version=finstance_version).exists():
                        continue
                    else:
                        xform_hist = XformHistory()
                        if finstance.project_fxf:
                            xform_hist.xform = finstance.project_fxf.xf
                            xform_hist.title = finstance.project_fxf.xf.title
                            xform_hist.uuid = finstance.project_fxf.xf.uuid
                            
                        else:
                            xform_hist.xform = finstance.site_fxf.xf
                            xform_hist.title = finstance.site_fxf.xf.title
                            xform_hist.uuid = finstance.site_fxf.xf.uuid
                        
                        xform_hist.version = finstance.version
                        xform_hist.save()
                        print('Finstance version not matching in xform and xform history.', finstance.id)
            else:
                stop = True

            offset += batchsize
                        

