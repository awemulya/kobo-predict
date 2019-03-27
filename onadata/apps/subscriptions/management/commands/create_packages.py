from django.core.management.base import BaseCommand
from onadata.apps.subscriptions.models import Package


class Command(BaseCommand):
    help = 'Create default packages'

    def handle(self, *args, **options):

        PLAN_CHOICES = {
            0:
                 {'Free':
                      {'submission': 250, 'extra_submissions_charge': 0, 'total_charge': 0, 'period_type': 0}
                  }
             ,
            1:
                 {'Basic Monthly Plan':
                      {'submission': 500, 'extra_submissions_charge': 0.2, 'total_charge': 100, 'period_type': 1}
                  }
             ,
            2:
                 {'Basic Yearly Plan':
                      {'submission': 6000, 'extra_submissions_charge': 0.25, 'total_charge': 1000, 'period_type': 2}
                  }
             ,
            3:
                 {'Extended Monthly Plan':
                      {'submission': 2500, 'extra_submissions_charge': 0.22, 'total_charge': 500, 'period_type': 1}
                  }
             ,
            4:
                 {'Extended Yearly Plan':
                      {'submission': 30000, 'extra_submissions_charge': 0.22, 'total_charge': 5000, 'period_type': 2}
                  }
             ,
            5:
                 {'Pro Monthly Plan':
                      {'submission': 5000, 'extra_submissions_charge': 0.2, 'total_charge': 1000, 'period_type': 1}
                  }
             ,
            6:
                 {'Pro Yearly Plan':
                      {'submission': 60000, 'extra_submissions_charge': 0.2, 'total_charge': 10000, 'period_type': 2}
                  }
             ,
            7:
                 {'Scale Monthly Plan':
                      {'submission': 15000, 'extra_submissions_charge': 0.15, 'total_charge': 3000, 'period_type': 1}
                  }
             ,
            8:
                 {'Scale Yearly Plan':
                      {'submission': 40, 'extra_submissions_charge': 0.15, 'total_charge': 800, 'period_type': 2}
                  }
            ,
            9:
                {'Starter Monthly Plan':
                     {'submission': 100, 'extra_submissions_charge': 0.25, 'total_charge': 20, 'period_type': 1}
                 }
            ,
            10:
                {'Starter Yearly Plan':
                     {'submission': 1200, 'extra_submissions_charge': 0.25, 'total_charge': 200, 'period_type': 2}
                 }


        }

        for key, value in PLAN_CHOICES.items():

            package, created = Package.objects.get_or_create(plan=key, submissions=PLAN_CHOICES[key][value.keys()[0]]['submission'],
                                                             extra_submissions_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['extra_submissions_charge'], total_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['total_charge'], period_type=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['period_type'])
            self.stdout.write('Successfully created package .. "%s"' % str(package))
