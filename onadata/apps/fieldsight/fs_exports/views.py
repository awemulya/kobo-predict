from __future__ import unicode_literals
import xlwt
from .. models import Project, Site
from .. rolemixins import DonorRoleMixin, ProjectRoleMixin
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
        region_id = self.kwargs.get('region_id', None)
        sites = project.sites.all().order_by('identifier')

        if region_id:
            sites = project.sites.filter(region_id=region_id).order_by('identifier')

        for site in sites:
            column = [site.identifier, site.name, site.type.identifier, site.phone, site.address, site.public_desc, site.additional_desc, site.latitude,
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


class CloneProjectSites(ProjectRoleMixin, View):
    def post(self, *args, **kwargs):
        f_project=get_object_or_404(Project, pk=self.kwargs.get('pk'))
        t_project=get_object_or_404(Project, pk=self.kwargs.get('t_pk'))
        region_id = self.kwargs.get('region_id', None)

        meta_attributes = self.request.boby.get('meta_attributes')
        regions = self.request.boby.get('regions')
        ignore_region = self.request.bofy.get('ignore_region')
        
        def filterbyquestion_name(seq, value):
            for el in seq:
                if (not meta_attributes) or (meta_attributes and el.get('question_name') in meta_attributes)
                    if el.get('question_name')==value:
                        return True
            return False
        
        # migrate metas
        if t_project.site_meta_attributes:
            t_metas = t_project.site_meta_attributes
            f_metas = t_project.site_meta_attributes

            for f_meta in f_metas:
                check = filterbyquestion_name(t_metas, f_meta.get('question_name'))
                if not check:
                    t_metas.append(f_meta)

        region_map = {}

        def get_t_region_id(f_region_id):
            # To get new region id without a query
            if f_region_id is not None and f_region_id in region_map:
                return region_map[f_region_id]
            else:
                return None
        
        # migrate regions
        if f_projec.cluster_sites and not ignore_region:
            
            t_project_regions = t_project.regions.all().values_list('identifier', flat=True)
            t_project.cluster_sites=True
            
            # To handle whole project or a single region migrate
            regions = f_project.regions.filter(region_id__in=regions)

            for region in regions:
                f_region_id = region.id
                if region.identifier in t_project_regions:
                    t_region_id = project.regions.get(identifier=region.identifier).id
                else:
                    region.id=None
                    region.project_id=t_project.id
                    region.save()
                    t_region_id = region.id
                region_map[f_region_id]=t_region_id
        
        t_project.save()

        # migrate sites
        t_project_sites = t_project.sites.all().values_list('identifier', flat=True)

        if f_project.cluster_sites and not ignore_region:
            sites = f_project.sites.filter(region_id=regions)
          
            if 0 in regions:
                unassigned_sites = f_project.sites.filter(region_id=None)
                sites = sites | unassigned_sites

        else:
            sites = f_project.sites.all()


        for site in sites:
            site.id = None
            site.project_id = t_project_id
            
            if site.identifier in t_project_sites:
                site.identifier = str(site.identifier) + "IFP" + str(f_project.id)
        
            if f_project.cluster_sites and not ignore_region:
                site.region_id = get_t_region_id(site.region_id)
            else:
                site.region_id = None
            
            site.save()
        return None
