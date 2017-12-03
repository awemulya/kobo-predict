import json
from django.db.models import Q
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.views.generic import ListView, TemplateView
from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage

from onadata.apps.users.models import UserProfile

from onadata.apps.fieldsight.mixins import OrganizationMixin

from rest_framework import routers, serializers, viewsets
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.eventlog.models import FieldSightLog, CeleryTaskProgress
from rest_framework.pagination import PageNumberPagination
from onadata.apps.fieldsight.rolemixins import LoginRequiredMixin
from django.db.models import Q

from django.http import JsonResponse
from celery.result import AsyncResult

class LogSerializer(serializers.ModelSerializer):
    source_uid = serializers.ReadOnlyField(source='source_id', read_only=True)
    source_name = serializers.ReadOnlyField(source='source.username', read_only=True)
    source_img = serializers.ReadOnlyField(source='source.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    
    get_event_name = serializers.ReadOnlyField()
    get_event_url = serializers.ReadOnlyField()

    get_extraobj_name = serializers.ReadOnlyField()
    get_extraobj_url = serializers.ReadOnlyField()

    get_absolute_url = serializers.ReadOnlyField()
    
    # org_name = serializers.ReadOnlyField(source='organization.name', read_only=True)
    # get_org_url = serializers.ReadOnlyField()

    # project_name = serializers.ReadOnlyField(source='project.name', read_only=True)
    # get_project_url = serializers.ReadOnlyField()

    # site_name = serializers.ReadOnlyField(source='site.name', read_only=True)
    # get_site_url = serializers.ReadOnlyField()

    class Meta:
        model = FieldSightLog
        exclude = ('title', 'description', 'is_seen', 'content_type', 'organization', 'project', 'site', 'object_id', 'extra_object_id', 'source', 'extra_content_type',)




class NotificationListView(OrganizationMixin, ListView):
    model = FieldSightLog
    paginate_by = 100

    def get_queryset(self):
        return super(NotificationListView, self).get_queryset().order_by('-date')

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = FieldSightLog.objects.select_related('source__user_profile').all().prefetch_related('seen_by')
    serializer_class = LogSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        if self.request.role.group.name == "Super Admin":
            return queryset 
        org_ids = self.request.roles.filter(group__name='Organization Admin').values('organization_id')
        project_ids = self.request.roles.filter(group__name='Project Manager').values('project_id')
        site_ids = self.request.roles.filter(Q(group__name='Site Supervisor') | Q(group__name='Reviewer')).values('site_id')
        return queryset.filter(Q(organization_id__in=org_ids) | Q(project_id__in=project_ids) | Q(site_id__in=site_ids) | Q(recipient_id=self.request.user.id))

class NotificationCountnSeen(View):
    def get(self, request):
        queryset = FieldSightLog.objects.filter(date__gt=request.user.user_profile.notification_seen_date).prefetch_related('seen_by')
        if request.role.group.name == "Super Admin":
            count = queryset.filter().exclude(seen_by__id=request.user.id).count()       
        else:
            org_ids = request.roles.filter(group__name='Organization Admin').values('organization_id')
            project_ids = request.roles.filter(group__name='Project Manager').values('project_id')
            site_ids = request.roles.filter(Q(group__name='Site Supervisor') | Q(group__name='Reviewer')) .values('site_id')
            count = queryset.filter(Q(organization_id__in=org_ids) | Q(project_id__in=project_ids) | Q(site_id__in=site_ids)).exclude(seen_by__id=request.user.id).count()
        data = {
            'id': request.user.id,
            'count': count,
        }
        return JsonResponse(data)

    def post(self, request):
        # print request.user.user_profile.notification_seen_date
        profile = UserProfile.objects.get(user_id=request.user.id)
        profile.notification_seen_date = now()
        profile.save()
        data = {
            'status': 'Sucess',
            'seen_time_stamp': str(now()),
        }
        return JsonResponse(data)


class MessageListView(ListView):
    model = FieldSightMessage
    paginate_by = 100

    def get_queryset(self):
        return super(MessageListView, self).get_queryset().filter(Q(sender=self.request.user) | Q(receiver=self.request.user))


class NotificationDetailView(View):
    def get(self, request, *args, **kwargs):
        notification = FieldSightLog.objects.get(pk=kwargs.get('pk'))
        if not notification.seen_by.filter(id=request.user.id).exists():
            notification.seen_by.add(request.user)
        if notification.type == 0:
            return redirect('/users/profile/{}'.format(notification.content_object.user.id))
        url =  notification.content_object.get_absolute_url()
        return redirect(url)

class CeleryTaskProgressView(View):
    """ A view to report the progress to the user """
    def get(self, request, *args, **kwargs):
        if 'task_id' in request.GET:
            task_id = request.GET['task_id']
        else:
            data = {
            'status': 'No Task Id given.',
            }
            return JsonResponse(data)

        task = AsyncResult(task_id)
        data = task.result or task.state
        return JsonResponse(data)


class MyCeleryTaskProgress(TemplateView):
    def get(self, request, *args, **kwargs):
        pending = CeleryTaskProgress.objects.filter(user_id = request.user.id, status=0)
        ongoing = CeleryTaskProgress.objects.filter(user_id = request.user.id, status=1)
        completed = CeleryTaskProgress.objects.filter(user_id = request.user.id, status=2)
        failed = CeleryTaskProgress.objects.filter(user_id = request.user.id, status=3)
        return render(request, 'eventlog/fieldsight_task_list.html',{'pending':pending, 'ongoing':ongoing, 'completed': completed, 'failed':failed })


