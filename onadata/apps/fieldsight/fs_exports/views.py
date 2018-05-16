from __future__ import unicode_literals
import xlwt
from .. models import Project, Site
from .. rolemixins import DonorRoleMixin
from django.views.generic import TemplateView, View
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


class ExportProjectSites(DonorRoleMixin, View):
    def get(self, *args, **kwargs):
        project=get_object_or_404(Project, pk=self.kwargs.get('pk'))
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="bulk_upload_sites.xls"'
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Sites')
        # Sheet header, first row
        row_num = 0
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        columns = ['identifier', 'name', 'type', 'phone', 'address', 'public_desc', 'additional_desc', 'latitude',
                   'longitude', ]
        if project.cluster_sites:
            columns += ['region_id', ]
        meta_ques = project.site_meta_attributes
        for question in meta_ques:
            columns += [question['question_name']]
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)
        row_num += 1

        font_style_unbold = xlwt.XFStyle()
        font_style_unbold.font.bold = False
        for site in project.sites.all():
            column = [site.identifier, site.name, site.type, site.phone, site.address, site.public_desc, site.additional_desc, site.latitude,
                       site.longitude, ]
            if project.cluster_sites:
                if site.region:
                    column += [site.region.identifier, ]
                else:
                    column += ['', ]
            meta_ques = project.site_meta_attributes
            meta_ans = site.site_meta_attributes_ans
            for question in meta_ques:
                if question['question_name'] in meta_ans:
                    column += [meta_ans[question['question_name']]]
                else:
                    column += ['']
            for col_num in range(len(column)):
                ws.write(row_num, col_num, column[col_num], font_style_unbold)
            row_num += 1
        wb.save(response)
        return response
