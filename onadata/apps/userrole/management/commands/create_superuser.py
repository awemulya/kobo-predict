from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from onadata.apps.userrole.models import UserRole
from django.contrib.auth import get_user_model
from django.conf import settings




class Command(BaseCommand):
    help = 'Create superuser'

    def add_arguments(self, parser):
        parser.add_argument('email_address', type=str)

    def handle(self, *args, **options):
        email_address = options['email_address']
        self.stdout.write(email_address)
        super_admin = Group.objects.get(name="Super Admin")

        if User.objects.filter(email=email_address).count():
            user = User.objects.get(email=email_address)
            self.stdout.write('email found')
            new_group, created = UserRole.objects.get_or_create(user=user, group=super_admin)
            self.stdout.write('new super admin role created for email')

        else:
            self.stdout.write('email not found.. "%s"',email_address),



 




