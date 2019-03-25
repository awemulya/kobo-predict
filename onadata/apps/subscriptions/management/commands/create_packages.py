from django.core.management.base import BaseCommand
from onadata.apps.subscriptions.models import Package


class Command(BaseCommand):
    help = 'Create default packages'

    def handle(self, *args, **options):

        PLAN_CHOICES = {
            0:
                 {'Free':
                      {'submission': 3, 'extra_submissions_charge': 0, 'total_charge': 0, 'period_type': 0}
                  }
             ,
            1:
                 {'Basic Monthly':
                      {'submission': 5, 'extra_submissions_charge': 0.25, 'total_charge': 100, 'period_type': 1}
                  }
             ,
            2:
                 {'Basic Yearly':
                      {'submission': 10, 'extra_submissions_charge': 0.25, 'total_charge': 200, 'period_type': 2}
                  }
             ,
            3:
                 {'Extended Monthly':
                      {'submission': 15, 'extra_submissions_charge': 0.22, 'total_charge': 300, 'period_type': 1}
                  }
             ,
            4:
                 {'Extended Yearly':
                      {'submission': 20, 'extra_submissions_charge': 0.22, 'total_charge': 400, 'period_type': 2}
                  }
             ,
            5:
                 {'Pro Monthly':
                      {'submission': 25, 'extra_submissions_charge': 0.2, 'total_charge': 500, 'period_type': 1}
                  }
             ,
            6:
                 {'Pro Yearly':
                      {'submission': 30, 'extra_submissions_charge': 0.2, 'total_charge': 600, 'period_type': 2}
                  }
             ,
            7:
                 {'Scale Monthly':
                      {'submission': 35, 'extra_submissions_charge': 0.15, 'total_charge': 700, 'period_type': 1}
                  }
             ,
            8:
                 {'Scale Yearly':
                      {'submission': 40, 'extra_submissions_charge': 0.15, 'total_charge': 800, 'period_type': 2}
                  }
            ,
            9:
                {'Starter Monthly':
                     {'submission': 3, 'extra_submissions_charge': 0.3, 'total_charge': 50, 'period_type': 1}
                 }
            ,
            10:
                {'Starter Yearly':
                     {'submission': 4, 'extra_submissions_charge': 0.29, 'total_charge': 75, 'period_type': 2}
                 }


        }

        for key, value in PLAN_CHOICES.items():

            package, created = Package.objects.get_or_create(plan=key, submissions=PLAN_CHOICES[key][value.keys()[0]]['submission'],
                                                             extra_submissions_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['extra_submissions_charge'], total_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['total_charge'], period_type=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['period_type'])
            self.stdout.write('Successfully created package .. "%s"' % str(package))
