from django.core.management.base import BaseCommand
from fcm.utils import get_device_model


class Command(BaseCommand):
    help = 'Delete_device'

    # def add_arguments(self, parser):
    #     parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        Device = get_device_model()
        if Device.objects.exists():
            Device.objects.all().delete()
        else:
            self.stdout.write('no device is present'),


