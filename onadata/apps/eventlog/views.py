from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import ListView, View

from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage
from onadata.apps.fieldsight.mixins import OrganizationMixin

from rest_framework import routers, serializers, viewsets
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.eventlog.models import FieldSightLog
from rest_framework.pagination import PageNumberPagination
from onadata.apps.fieldsight.rolemixins import LoginRequiredMixin
class LogSerializer(serializers.ModelSerializer):
    source_name = serializers.ReadOnlyField(source='source.user.first_name', read_only=True)
    source_img = serializers.ReadOnlyField(source='source.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    
    #event = serializers.ReadOnlyField(source='content_object', read_only=True)
    get_event_url = serializers.ReadOnlyField()

    org_name = serializers.ReadOnlyField(source='organization.name', read_only=True)
    get_org_url = serializers.ReadOnlyField()

    project_name = serializers.ReadOnlyField(source='project.name', read_only=True)
    get_project_url = serializers.ReadOnlyField()

    site_name = serializers.ReadOnlyField(source='site.name', read_only=True)
    get_site_url = serializers.ReadOnlyField()

    class Meta:
        model = FieldSightLog
        exclude = ('title', 'description', 'seen_by', 'content_type', 'organization', 'project', 'site', 'source', 'object_id')




class NotificationListView(OrganizationMixin, ListView):
    model = FieldSightLog
    paginate_by = 100

    def get_queryset(self):
        return super(NotificationListView, self).get_queryset().order_by('-date')

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 2

class NotificationViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = FieldSightLog.objects.all()
    serializer_class = LogSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        return queryset.filter(id=38)


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



