from django.core.management.base import BaseCommand
from onadata.apps.subscriptions.models import Package


class Command(BaseCommand):
    help = 'Create default packages'

    def handle(self, *args, **options):

        PLAN_CHOICES = {
            0:
                 {'Free':
                      {'submission': 1000, 'extra_submissions_charge': 0}
                  }
             ,
            1:
                 {'Basic Monthly':
                      {'submission': 5000, 'extra_submissions_charge': 0.25}
                  }
             ,
            2:
                 {'Basic Yearly':
                      {'submission': 5000, 'extra_submissions_charge': 0.25}
                  }
             ,
            3:
                 {'Extended Monthly':
                      {'submission': 20000, 'extra_submissions_charge': 0.22}
                  }
             ,
            4:
                 {'Extended Yearly':
                      {'submission': 20000, 'extra_submissions_charge': 0.22}
                  }
             ,
            5:
                 {'Pro Monthly':
                      {'submission': 50000, 'extra_submissions_charge': 0.2}
                  }
             ,
            6:
                 {'Pro Yearly':
                      {'submission': 50000, 'extra_submissions_charge': 0.2}
                  }
             ,
            7:
                 {'Scale Monthly':
                      {'submission': 150000, 'extra_submissions_charge': 0.15}
                  }
             ,
            8:
                 {'Scale Yearly':
                      {'submission': 150000, 'extra_submissions_charge': 0.15}
                  }


        }

        for key, value in PLAN_CHOICES.items():

            package, created = Package.objects.get_or_create(plan=key, submissions=PLAN_CHOICES[key][value.keys()[0]]['submission'],
                                                             extra_submissions_charge=PLAN_CHOICES[key][value.keys()[0]]
                                                             ['extra_submissions_charge'])
            self.stdout.write('Successfully created package .. "%s"' % str(package))
