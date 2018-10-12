from collections import OrderedDict

from django.db.models import Count, Case, When, IntegerField, Sum

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
        
        data = Site.objects.aggregate(
             first=Sum(
                 Case(When(current_progress__lt = 10, then=1),
                      output_field=IntegerField())
             ),
             second=Sum(
                 Case(When(current_progress__gte=20, current_progress__lt=40, then=1),
                      output_field=IntegerField())
             ),
             third=Sum(
                 Case(When(current_progress__gte=40, current_progress__lt=60, then=1),
                      output_field=IntegerField())
             ),
             fourth=Sum(
                 Case(When(current_progress__gte=60, current_progress__lt=80, then=1),
                      output_field=IntegerField())
             ),
             fifth=Sum(
                 Case(When(current_progress__gte=80, current_progress__lt=100, then=1),
                      output_field=IntegerField())
             ),
            sixth=Sum(
                 Case(When(current_progress=100, then=1),
                      output_field=IntegerField())
             )
        )

        self.data['< 20'] = 0 if data['first'] is None else data['first']
        self.data['20 - 40'] = 0 if data['second'] is None else data['second']
        self.data['40 - 60'] = 0 if data['third'] is None else data['third']
        self.data['60 - 80'] = 0 if data['fourth'] is None else data['fourth']
        self.data['80 <'] = 0 if data['fifth'] is None else data['fifth']
        self.data['Completed'] = 0 if data['sixth'] is None else data['sixth']
        


        

