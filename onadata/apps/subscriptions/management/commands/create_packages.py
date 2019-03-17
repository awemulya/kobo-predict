from django.core.management.base import BaseCommand
from onadata.apps.subscriptions.models import Package


class Command(BaseCommand):
    help = 'Create default packages'

    def handle(self, *args, **options):

        PLAN_CHOICES = {
            0:
                 {'Free':
                      {'submission': 1000, 'extra_submissions_charge': 0, 'total_charge': 0}
                  }
             ,
            1:
                 {'Basic Monthly':
                      {'submission': 5000, 'extra_submissions_charge': 0.25, 'total_charge': 100}
                  }
             ,
            2:
                 {'Basic Yearly':
                      {'submission': 5000, 'extra_submissions_charge': 0.25, 'total_charge': 1000}
                  }
             ,
            3:
                 {'Extended Monthly':
                      {'submission': 20000, 'extra_submissions_charge': 0.22, 'total_charge': 500}
                  }
             ,
            4:
                 {'Extended Yearly':
                      {'submission': 20000, 'extra_submissions_charge': 0.22, 'total_charge': 5000}
                  }
             ,
            5:
                 {'Pro Monthly':
                      {'submission': 50000, 'extra_submissions_charge': 0.2, 'total_charge': 1000}
                  }
             ,
            6:
                 {'Pro Yearly':
                      {'submission': 50000, 'extra_submissions_charge': 0.2, 'total_charge': 10000}
                  }
             ,
            7:
                 {'Scale Monthly':
                      {'submission': 150000, 'extra_submissions_charge': 0.15, 'total_charge': 3000}
                  }
             ,
            8:
                 {'Scale Yearly':
                      {'submission': 150000, 'extra_submissions_charge': 0.15, 'total_charge': 30000}
                  }


        }

        for key, value in PLAN_CHOICES.items():

            package, created = Package.objects.get_or_create(plan=key, submissions=PLAN_CHOICES[key][value.keys()[0]]['submission'],
                                                             extra_submissions_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['extra_submissions_charge'], total_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['total_charge'])
            self.stdout.write('Successfully created package .. "%s"' % str(package))
