from __future__ import unicode_literals

import os
import glob
import shutil

from django.core.files import File

from django.core.management.base import BaseCommand
from onadata.apps.fsforms.models import XformHistory
from onadata.apps.logger.models import XForm

from pyxform.builder import create_survey_from_xls


import os
import glob
import csv
from xlsxwriter.workbook import Workbook

from onadata.koboform.pyxform_utils import convert_csv_to_xls


def csv_to_xls(dir_name):
    for csvfile in glob.glob(os.path.join(dir_name, '*.csv')):
        workbook = Workbook(csvfile[:-4] + '.xlsx')
        worksheet = workbook.add_worksheet()
        with open(csvfile, 'rt', encoding='utf8') as f:
            reader = csv.reader(f)
            for r, row in enumerate(reader):
                for c, col in enumerate(row):
                    worksheet.write(r, c, col)
        workbook.close()



def get_version(xml):
    import re
    p = re.compile('version="(.*)">')
    m = p.search(xml)
    if m:
        return m.group(1)
    raise Exception("no version found")


def get_id_string(xml):
    import re
    p = re.compile('id="(.*)" ')
    m = p.search(xml)
    if m:
        return m.group(1)
    raise Exception("no id string found")


class Command(BaseCommand):
    help = 'Create xml from xls'
    
    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)

    def handle(self, *args, **options):
        # xls_directory = "/home/xls"
        xls_directory = options['directory']
        error_file_list = []
        # csv_to_xls(xls_directory)
        for filename in os.listdir(xls_directory):
            if os.path.isfile(os.path.join(xls_directory,filename)):
                if filename.endswith(".xls"):
                    pass
                elif filename.endswith(".csv"):
                    pass
                else:
                    print("##########################")
                    print("##########################")
                    print("Differentt format file", filename)
                    print("##########################")
                    print("##########################")
                    continue
            xls_file = open(os.path.join(xls_directory, filename))
            print("creating survey for ", xls_file)
            try:
                survey = create_survey_from_xls(xls_file)
            
            except Exception as e:
                error_file_list.append(filename)
                pass
            xml = survey.to_xml()
            xls_file.close()
            version = get_version(xml)
            # print("version =  ======", version)
            id_string = get_id_string(xml)
            if not XForm.objects.filter(id_string=id_string).exists():
                print("xform with id string not found ", id_string)
                continue
            xform = XForm.objects.get(id_string=id_string)
            xform_version = get_version(xform.xml)
            if version == xform_version:
                print("##########################")
                print("##########################")
                print("this file is current version of Xform", filename, "Ignored")
                print("##########################")
                print("##########################")
                continue
            if not XformHistory.objects.filter(xform=xform, version=version).exists():
                print("creating history from file ", filename)
                file_obj = open(os.path.join(xls_directory, filename))
                history = XformHistory(xform=xform, xls=File(file_obj))
                history.save()
            else:
                print('History already exists of this file  ', filename)
            print('Successfully created XFORM HISTORY form  ', filename)
        
        if error_file_list:
            print('Errors occured at files: ')
            for files in error_file_list:
                print(files)