import json
from datetime import datetime

from django.db.models import Q
from django.utils.timezone import now
from django.shortcuts import render, redirect
from django.views.generic import ListView, View
from django.views.generic import ListView, TemplateView
from onadata.apps.eventlog.models import FieldSightLog, FieldSightMessage, CeleryTaskProgress

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
from onadata.apps.eventlog.serializers.LogSerializer import NotificationSerializer, LogSerializer, TaskSerializer
from onadata.apps.fieldsight.rolemixins import ProjectRoleMixin, SiteRoleMixin, ReadonlySiteLevelRoleMixin, ReadonlyProjectLevelRoleMixin
from onadata.apps.fieldsight.models import Project, Site
from onadata.apps.userrole.models import UserRole

class NotificationListView(LoginRequiredMixin, ListView):
    model = FieldSightLog
    paginate_by = 100

    def get_queryset(self):
        return super(NotificationListView, self).get_queryset().order_by('-date')


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

class MyTaskListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = CeleryTaskProgress.objects.all()
    serializer_class = TaskSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):

        profile = self.request.user.user_profile
        current_filterdate = profile.task_last_view_date
        profile.task_last_view_date = datetime.now()
        profile.save()
        
        if self.request.group.name == "Super Admin":
            return queryset 

        return queryset.filter(user_id=self.request.user.id, date_updateded__gte = current_filterdate).order_by('date_updateded')

class OtherTaskListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = CeleryTaskProgress.objects.all()
    serializer_class = TaskSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        # if self.request.group.name == "Super Admin":
        #     return queryset 
        self_projects = UserRole.objects.filter(user_id=self.request.user.id, ended_at__isnull=False, project_id__isnull=False).distinct('project_id').values_list('project_id', flat=True)
        self_orgs = UserRole.objects.filter(user_id=self.request.user.id, ended_at__isnull=False, organization_id__isnull=False).distinct('organization_id').values_list('organization_id', flat=True)
        self_org_projects = Project.objects.filter(organization_id__in=self_orgs).only('id')
        return queryset.filter(Q(object_id__in=self_projects) | Q(object_id__in=self_org_projects), status=2, content_type__model="project").exclude(user_id=self.request.user.id).order_by('date_updateded')


class MyTaskListViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """

    queryset = CeleryTaskProgress.objects.all()
    serializer_class = TaskSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        if self.request.group.name == "Super Admin":
            return queryset 

        return queryset.filter(user_id=self.request.user.id)


class ProjectLog(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = FieldSightLog.objects.select_related('source__user_profile').filter(recipient=None)
    serializer_class = NotificationSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        return queryset.filter(Q(project_id=self.kwargs.get('pk')) | (Q(content_type=ContentType.objects.get(app_label="fieldsight", model="project")) & Q(object_id=self.kwargs.get('pk'))))


class SiteLog(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing sites.
    """
    queryset = FieldSightLog.objects.select_related('source__user_profile').filter(recipient=None)
    serializer_class = NotificationSerializer
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        site = Site.objects.get(pk=self.kwargs.get('pk'))
        content_site = ContentType.objects.get(app_label="fieldsight", model="site")
        project = site.project
        query = Q(site_id=self.kwargs.get('pk')) | (Q(content_type=content_site) & Q(object_id=self.kwargs.get('pk'))) | (Q(extra_content_type=content_site) & Q(extra_object_id=self.kwargs.get('pk')))
        meta_dict = {}
        for meta in project.site_meta_attributes:
            if meta['question_type'] == "Link" and meta['question_name'] in site.site_meta_attributes_ans:
                meta_site_id = Site.objects.filter(identifier=site.site_meta_attributes_ans[meta['question_name']], project_id=meta['project_id'])
                if meta_site_id:
                    selected_metas = [sub_meta['question_name'] for sub_meta in meta['metas'][str(meta['project_id'])]]
                    meta_dict[meta_site_id[0].id] = selected_metas

        for key, value in meta_dict.items():
            for item in value:
                query |= (Q(type=15) & Q(content_type=content_site) & Q(object_id=key) & Q(extra_json__contains='"'+item +'":'))

        return queryset.filter(query)

class NotificationCountnSeen(View):
    def get(self, request):
        queryset = FieldSightLog.objects.filter(date__gt=request.user.user_profile.notification_seen_date).prefetch_related('seen_by')
        if request.group.name == "Super Admin":
            count = queryset.filter().exclude(seen_by__id=request.user.id).count()       
            task_count = CeleryTaskProgress.objects.filter(status__in=[2,3], date_updateded__gte = request.user.user_profile.task_last_view_date).count()
        else:
            org_ids = request.roles.filter(group__name='Organization Admin').values('organization_id')
            project_ids = request.roles.filter(group__name='Project Manager').values('project_id')
            site_ids = request.roles.filter(Q(group__name='Site Supervisor') | Q(group__name='Reviewer')) .values('site_id')
            count = queryset.filter(Q(organization_id__in=org_ids) | Q(project_id__in=project_ids) | Q(site_id__in=site_ids)).exclude(seen_by__id=request.user.id).count()
            task_count = CeleryTaskProgress.objects.filter(status__in=[2,3], user_id = request.user.id, date_updateded__gte = request.user.user_profile.task_last_view_date).count()
        data = {
            'id': request.user.id,
            'count': count,
            'task_count': task_count
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


class ProjectLogListView(ReadonlyProjectLevelRoleMixin, TemplateView):
    template_name = "eventlog/loglist.html"

    def get_context_data(self, **kwargs):
        data = super(ProjectLogListView, self).get_context_data(**kwargs)
        project = Project.objects.get(pk=kwargs.get('pk'))
        data['is_project'] = True
        data['obj'] = project
        data['is_donor_only'] = kwargs.get('is_donor_only', False)
        return data

class SiteLogListView(ReadonlySiteLevelRoleMixin, TemplateView):
    template_name = "eventlog/loglist.html"

    def get_context_data(self, **kwargs):
        data = super(SiteLogListView, self).get_context_data(**kwargs)
        site = Site.objects.get(pk=kwargs.get('pk'))
        data['is_project'] = False
        data['obj'] = site
        data['is_donor_only'] = kwargs.get('is_donor_only', False)
        return data