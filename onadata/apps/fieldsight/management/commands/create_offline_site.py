from django.core.management.base import BaseCommand

from onadata.apps.fieldsight.models import Site


class Command(BaseCommand):
    help = 'Create default groups'

    def add_arguments(self, parser):
        parser.add_argument('project_id', type=int)

    def handle(self, *args, **options):
        project_id = options['project_id']
        self.stdout.write('Reading project id "%s"' % project_id)
        site, created = Site.objects.get_or_create(
            identifier="temporary_site",
            is_active=True,
            name="Temporary  Site",
            project_id=project_id,
            is_survey=False,
        )
        print("created ==== ", created, "site=", site.__dict__)
