from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from onadata.libs.utils.fieldsight_tools import clone_kpi_form


class Command(BaseCommand):
    help = 'Create default groups'

    def handle(self, *args, **options):
        clone_kpi_form('KPI_ID_STRING', 'USER_TOKEN', "FORM NAME")