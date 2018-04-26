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
from django.contrib.contenttypes.models import ContentType

from django.http import JsonResponse
from celery.result import AsyncResult
from onadata.apps.eventlog.serializers.LogSerializer import NotificationSerializer
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin, SiteRoleMixin

class NotificationListView(LoginRequiredMixin, TemplateView):
    template_name = "eventlog/fieldsight_notification_list.html"

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20

class SmallResultsSetPagination(PageNumberPagination):
    page_size = 8


class NotificationViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = FieldSightLog.objects.select_related('source__user_profile').all().prefetch_related('seen_by')
    serializer_class = NotificationSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        if self.request.group.name == "Super Admin":
            return queryset 
        org_ids = self.request.roles.filter(group__name='Organization Admin').values('organization_id')
        project_ids = self.request.roles.filter(group__name='Project Manager').values('project_id')
        site_ids = self.request.roles.filter(Q(group__name='Site Supervisor') | Q(group__name='Reviewer')).values('site_id')
        return queryset.filter(Q(organization_id__in=org_ids) | Q(project_id__in=project_ids) | Q(site_id__in=site_ids) | Q(recipient_id=self.request.user.id))


class ProjectLog(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = FieldSightLog.objects.select_related('source__user_profile').all().prefetch_related('seen_by')
    serializer_class = NotificationSerializer
    pagination_class = SmallResultsSetPagination

    def filter_queryset(self, queryset):
        return queryset.filter(Q(project_id=self.kwargs.get('pk')) | (Q(content_type=ContentType.objects.get(app_label="fieldsight", model="project")) & Q(object_id=self.kwargs.get('pk'))))


class SiteLog(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = FieldSightLog.objects.select_related('source__user_profile').all().prefetch_related('seen_by')
    serializer_class = NotificationSerializer
    pagination_class = SmallResultsSetPagination

    def filter_queryset(self, queryset):
        return queryset.filter(Q(site_id=self.kwargs.get('pk')) | (Q(content_type=ContentType.objects.get(app_label="fieldsight", model="site")) & Q(object_id=self.kwargs.get('pk'))))

class NotificationCountnSeen(View):
    def get(self, request):
        queryset = FieldSightLog.objects.filter(date__gt=request.user.user_profile.notification_seen_date).prefetch_related('seen_by')
        if request.group.name == "Super Admin":
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


class ProjectLogListView(ProjectRoleMixin, TemplateView):
    template_name = "eventlog/fieldsight_log_list.html"

    def get_context_data(self, **kwargs):
        data = super(ProjectLogListView, self).get_context_data(**kwargs)
        project = Project.objects.get(pk=kwargs.get('pk'))
        data['types'] = "Project"
        data['obj'] = project
        return data

class SiteLogListView(SiteRoleMixin, TemplateView):
    template_name = "eventlog/fieldsight_log_list.html"

    def get_context_data(self, **kwargs):
        data = super(SiteLogListView, self).get_context_data(**kwargs)
        site = Site.objects.get(pk=kwargs.get('pk'))
        data['types'] = "Site"
        data['obj'] = site
        return data