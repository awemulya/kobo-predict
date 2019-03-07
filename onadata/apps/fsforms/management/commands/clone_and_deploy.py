from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from onadata.libs.utils.fieldsight_tools import clone_kpi_form


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        clone_kpi_form('aRdfT8EeirMt8RZjCc779J', 'aaa192b3394953f24c21fcec865ae794dcf5d4b2', "hello World")