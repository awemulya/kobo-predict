from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User,Group
from onadata.apps.userrole.models import UserRole
from onadata.apps.staff.models import Bank
from django.contrib.auth import get_user_model
from django.conf import settings


   

class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        bank_list = ["Nepal Rastra Bank",
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
        
        for bank in bank_list:
            new_group, created = Bank.objects.get_or_create(name=bank)
            self.stdout.write('Successfully created bank .. "%s"' % bank)


 




