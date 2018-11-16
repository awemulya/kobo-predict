from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from pyxform.builder import create_survey_from_xls


class Command(BaseCommand):
    help = 'Create xml from xls'

    def _set_uuid_in_xml(self, file_name=None):
        """
        Add bind to automatically set UUID node in XML.
        """
        pass

    def handle(self, *args, **options):
        file_path = "/home/xls/a2bc3p3qUsADD2MDedAdSF"
        xls_file = open(file_path+".csv")
        survey = create_survey_from_xls(xls_file)
        xml = survey.to_xml()
        # xml = xml.encode('ascii', 'ignore').decode('ascii')
        print(xml)
        # f = open(file_path +".xml", "w+")
        # f.write(xml)
        # f.close()
        self.stdout.write('Successfully created xml ')