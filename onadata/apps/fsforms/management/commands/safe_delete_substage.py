from django.core.management.base import BaseCommand
from django.conf import settings

from onadata.apps.fsforms.models import Stage, FInstance


class Command(BaseCommand):
    help = 'Safely delete a substage and notify'

    def add_arguments(self, parser):
        parser.add_argument('substage_id', type=int)

    def handle(self, *args, **options):
        substage_id = options['substage_id']
        stage = Stage.objects.get(pk=substage_id)
        try:
            form = stage.stage_forms
            if FInstance.objects.filter(site_fxf=form).exists() or FInstance.objects.filter(project_fxf=form).exists():
                self.stdout.write('Substage form have submissions ! cant delete')
                return
            else:
                form.is_deleted = True
                form.stage = None
                form.save()
                stage.delete()
                self.stdout.write('Substage Deleted')
        except Exception as e:
            self.stdout.write('Substage have no Form')
            stage.delete()
            self.stdout.write('Substage Deleted')
