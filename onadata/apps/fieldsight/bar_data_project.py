from collections import OrderedDict

from django.db.models import Count, Case, When, IntegerField

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import FInstance, FieldSightXF


class BarGenerator(object):
    def __init__(self, sites):
        self.data = OrderedDict()
        self.data['Unstarted'] = 0
        self.data['< 20'] = 0
        self.data['20 - 40'] = 0
        self.data['40 - 60'] = 0
        self.data['60 - 80'] = 0
        self.data['80 <'] = 0
        self.data['Completed'] = 0

        for site in sites:
            progress_range = self.get_range(site.progress())
            self.data[progress_range] +=1

    def get_range(self, progress):
        if progress == 0: return self.data.keys()[0]
        if progress in range(1,20): return self.data.keys()[1]
        if progress in range(20,40): return self.data.keys()[2]
        if progress in range(40,60): return self.data.keys()[3]
        if progress in range(60,80): return self.data.keys()[4]
        if progress in range(80,100): return self.data.keys()[5]
        if progress == 100: return self.data.keys()[6]


class ProgressBarGenerator(object):
    def __init__(self, project):
        self.data = OrderedDict()
        self.data['Unstarted'] = 0
        self.data['< 20'] = 0
        self.data['20 - 40'] = 0
        self.data['40 - 60'] = 0
        self.data['60 - 80'] = 0
        self.data['80 <'] = 0
        self.data['Completed'] = 0

        sites = project.sites.all()

        site_data = {}
        site_forms = [] # unique forms submissions
        finstances = FInstance.objects.filter(site__project=project, form_status=3, site_fxf__is_staged=True)
        for finstance in finstances:
            if finstance.site_fxf not in site_forms:
                site_forms.append(finstance.site_fxf)
                if finstance.site.id not in site_data:
                    site_data[finstance.site.id] = 1
                else:
                    site_data[finstance.site.id] += 1



        self.site_data = site_data
        site_ids = self.site_data.keys()

        stage_forms = FieldSightXF.objects.filter(is_deleted=False, is_staged=True, is_deployed=True, site__id__in=site_ids)
        [sf for sf in stage_forms]
        site_stages_dict = {}
        for stage_form in stage_forms:
            if stage_form.site.id not in site_stages_dict:
                site_stages_dict[stage_form.site.id] = 1
            else:
                site_stages_dict[stage_form.site.id] += 1

        for site_id in site_ids:
            stages = site_stages_dict[site_id]
            approved = site_data[site_id]
            progress_range = self.get_progress_range(stages, approved)
            self.data[progress_range] += 1

        unstarted = Site.objects.filter(project=project, is_active=True, is_survey=False).count() - len(site_ids)

        self.data['Unstarted'] = unstarted


    def get_range(self, site):
        progress = site.stages_count / site.approved_count
        if progress == 0: return self.data.keys()[0]
        if progress in range(1,20): return self.data.keys()[1]
        if progress in range(20,40): return self.data.keys()[2]
        if progress in range(40,60): return self.data.keys()[3]
        if progress in range(60,80): return self.data.keys()[4]
        if progress in range(80,100): return self.data.keys()[5]
        if progress == 100: return self.data.keys()[6]

    def get_progress_range(self, stages, approved):
        if stages and approved:
            progress = stages / approved
        else:
            progress = 0
        if progress == 0: return self.data.keys()[0]
        if progress in range(1,20): return self.data.keys()[1]
        if progress in range(20,40): return self.data.keys()[2]
        if progress in range(40,60): return self.data.keys()[3]
        if progress in range(60,80): return self.data.keys()[4]
        if progress in range(80,100): return self.data.keys()[5]
        if progress == 100: return self.data.keys()[6]
