from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile
from django.contrib.auth import get_user_model
from django.conf import settings


   ["Nepal Rastra Bank",
    "Nepal Bank Limited",
    "Rastriya Banijya Bank Limited",
    "Agriculture Development Bank Limited",
    "Nabil Bank Limited",
    "Nepal Investment Bank Limited",
    "Standard Chartered Bank Nepal Limited",
    "Himalayan Bank Limited",
    "Nepal SBI Limited",
    "Nepal Bangladesh Bank Limited",
    "Everest Bank Limited",
    "Bank of Kathmandu Lumbini Limited",
    "Nepal Credit and Commerce Bank Limited",
    "Kumari Bank Limited",
    "Laxmi Bank Limited",
    "Siddhartha Bank Limited",
    "Global IME Bank Limited",
    "Citizens Bank International Limited",
    "Prime Commercial Bank Limited",
    "Sunrise Bank Limited",
    "NMB Bank Nepal Limited",
    "NIC Asia Bank Limited",
    "Machhapuchchhre Bank Limited",
    "Mega Bank Nepal Limited",
    "Civil Bank Limited",
    "Century Bank Limited",
    "Sanima Bank Limited",
    "Janata Bank Nepal Limited",
    "Prabhu Bank Limited"]

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
            UserProfile.objects.get_or_create(user=user)
            self.stdout.write('email found')
            new_group, created = UserRole.objects.get_or_create(user=user, group=super_admin)
            self.stdout.write('new super admin role created for email')

        else:
            self.stdout.write('email not found.. "%s"',email_address),



 




