from django.core.management.base import BaseCommand, CommandError
import reversion

from onadata.apps.logger.models import Instance


class Command(BaseCommand):
    help = 'Create version of submissions'

    def handle(self, *args, **options):
        id_string = "aq6BX3GMavXWWv5NdCcapK"
        submissions = Instance.objects.filter(xform__id_string=id_string)
        print(len(submissions))
        for s in submissions:
            with reversion.create_revision():
                s.save()
                reversion.set_user(s.user)
                reversion.set_comment("Created revision 2")