from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, View

from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage
from onadata.apps.fieldsight.mixins import OrganizationMixin


class NotificationListView(OrganizationMixin, ListView):
    model = FieldSightLog
    paginate_by = 10

    def get_queryset(self):
        return super(NotificationListView, self).get_queryset().order_by('is_seen')


class MessageListView(ListView):
    model = FieldSightMessage
    paginate_by = 10

    def get_queryset(self):
        return super(MessageListView, self).get_queryset().filter(Q(sender=self.request.user) | Q(receiver=self.request.user))


class NotificationDetailView(View):
    def get(self, request, *args, **kwargs):
        notification = FieldSightLog.objects.get(pk=kwargs.get('pk'))
        if not notification.is_seen:
            notification.is_seen = True
            notification.save()
        url =  notification.content_object.get_absolute_url()
        return redirect(url)



