import os
from onadata.settings.local_settings import XML_VERSION_MAX_ITER
from onadata.apps.fsforms.models import XformHistory
from django.core.management.base import BaseCommand
import re
import datetime

def check_version(instance, n):
    for i in range(n, 0, -1):
        p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version__00{0}" """.format(i))
        m = p.search(instance)
        if m:
            return m.group(1)

            
class Command(BaseCommand):
    help = 'Fix FInstance version for multiple versions in xml'

    # def add_arguments(self, parser):
    #     parser.add_argument('--file', type=str)

    def handle(self, *args, **options):
        batchsize = options.get("batchsize", 100)
        stop = False
        offset = 0
        while stop is not True:
            limit = offset + batchsize
            xformhists = XformHistory.objects.all()[offset:limit]
            inst = list(xformhists)
            if xformhists:
                self.stdout.write("Updating instances from #{} to #{}\n".format(
                        inst[0].id,
                        inst[-1].id))
                
                for xformhist in xformhists:
                    version = ''
                    n = XML_VERSION_MAX_ITER
                    xml = xformhist.xml
                    version = check_version(xml, n)
                    if version:
                        xformhist.version = version

                    if not version:
                        p = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/_version_" """)
                        m = p.search(xml)
                        if m:
                            xformhist.version = m.group(1)
                        
                        else:
                            p1 = re.compile("""<bind calculate="\'(.*)\'" nodeset="/(.*)/__version__" """)
                            m1 = p1.search(xml)
                            if m1:
                                xformhist.version = m1.group(1)
            else:
                stop = True

            offset += batchsize