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
        sites_with_stages_submitted = FInstance.objects.filter(site__project=project, form_status=3,
                                                               site_fxf__is_staged=True).distinct('site').count()
        self.data = OrderedDict()
        self.data['Unstarted'] = sites_with_stages_submitted
        self.data['< 20'] = 0
        self.data['20 - 40'] = 0
        self.data['40 - 60'] = 0
        self.data['60 - 80'] = 0
        self.data['80 <'] = 0
        self.data['Completed'] = 0
        sites = project.sites.all()

        for s in sites:
            if s.current_progress < 20:
                self.data['< 20']  += 1
            elif 40 > s.current_progress >= 20:
                self.data['20 - 40'] += 1
            elif 60 > s.current_progress >= 40:
                self.data['40 - 60'] += 1
            elif 80 > s.current_progress >= 60:
                self.data['60 - 80'] += 1
            elif 100 > s.current_progress >= 80:
                self.data['80 <'] += 1
            elif s.current_progress == 100:
                self.data['Completed'] += 1

