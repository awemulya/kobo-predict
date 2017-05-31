from django.shortcuts import render
from django.views.generic import ListView

from onadata.apps.eventlog.models import FieldSightLog
from onadata.apps.fieldsight.mixins import OrganizationMixin


class NotificationListView(OrganizationMixin, ListView):
    model = FieldSightLog
    paginate_by = 10

