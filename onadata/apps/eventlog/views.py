from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, View

from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage
from onadata.apps.fieldsight.mixins import OrganizationMixin

from rest_framework import routers, serializers, viewsets
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.eventlog.models import FieldSightLog

class LogSerializer(serializers.ModelSerializer):
    source_img = serializers.ReadOnlyField(source='source.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    #action_url = serializers.SerializerMethodField('self.get_event_url', read_only=True)
    get_event_url = serializers.ReadOnlyField()
    class Meta:
        model = FieldSightLog
        exclude = ()
class NotificationListView(OrganizationMixin, ListView):
    model = FieldSightLog
    paginate_by = 100

    def get_queryset(self):
        return super(NotificationListView, self).get_queryset().order_by('-date')

class NotificationViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = FieldSightLog.objects.filter(pk=25)
    serializer_class = LogSerializer

class MessageListView(ListView):
    model = FieldSightMessage
    paginate_by = 100

    def get_queryset(self):
        return super(MessageListView, self).get_queryset().filter(Q(sender=self.request.user) | Q(receiver=self.request.user))


class NotificationDetailView(View):
    def get(self, request, *args, **kwargs):
        notification = FieldSightLog.objects.get(pk=kwargs.get('pk'))
        if not notification.is_seen:
            notification.is_seen = True
            notification.save()
        if notification.type == 0:
            return redirect('/users/profile/{}'.format(notification.content_object.user.id))
        url =  notification.content_object.get_absolute_url()
        return redirect(url)



