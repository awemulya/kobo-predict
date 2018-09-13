from __future__ import unicode_literals

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, serializers
from rest_framework.pagination import PageNumberPagination

from onadata.apps.fieldsight.models import Site
from onadata.apps.fsforms.models import Stage, FieldSightXF, FInstance
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormSerializer, FSXFAllDetailSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10


class FieldSightXFormViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Fieldsight Xform.
    """
    queryset = FieldSightXF.objects.all()
    serializer_class = FSXFormSerializer


class SurveyFormsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    General Forms
    """
    queryset = FieldSightXF.objects.filter(is_staged=False, is_scheduled=False, is_deleted=False, is_survey=True)
    serializer_class = FSXFormSerializer
    # pagination_class = LargeResultsSetPagination

    def get_serializer_context(self):
        instances = []
        is_project = self.kwargs.get("is_project")
        pk = self.kwargs.get("pk")
        if is_project == "1":
            instances = FInstance.objects.filter(project__isnull=False,
                                                 project__id=pk,
                                                 project_fxf__is_survey=True
                                                 ).order_by('-pk').select_related("project", "project_fxf")
        if is_project == "0":
            instances = []
        self.kwargs.update({'instances': instances})
        return self.kwargs

    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        is_project = self.kwargs.get('is_project', None)
        pk = self.kwargs.get('pk', None)
        if is_project == "1":
            queryset = queryset.filter(project__id=pk)
        else:
            queryset = queryset.filter(site__id=pk)
        return queryset


class GeneralFormsViewSet(viewsets.ModelViewSet):
    """
    General Forms
    """
    queryset = FieldSightXF.objects.filter(is_staged=False, is_scheduled=False, is_deleted=False, is_survey=False)
    serializer_class = FSXFormSerializer
    # pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        is_project = self.kwargs.get('is_project', None)
        pk = self.kwargs.get('pk', None)
        if is_project == "1":
            queryset = queryset.filter(project__id=pk)
        else:
            project_id = get_object_or_404(Site, pk=pk).project.id
            queryset = queryset.filter(Q(site__id=pk, from_project=False)
                                       |Q(project__id=project_id))
        return queryset.select_related('xf', 'em').prefetch_related("site_form_instances", "project_form_instances")

    def get_serializer_context(self):
        instances = []
        is_project = self.kwargs.get("is_project")
        pk = self.kwargs.get("pk")
        if is_project == "1":
            instances = FInstance.objects.filter(project__isnull=False,
                                                 project__id=pk,
                                                 project_fxf__is_staged=False,
                                                 project_fxf__is_scheduled=False,
                                                 project_fxf__is_survey=False
                                                 ).order_by('-pk').select_related("project", "project_fxf")
        if is_project == "0":
            instances = FInstance.objects.filter(site__id=pk).order_by('-pk').select_related("site", "site_fxf")
        self.kwargs.update({'instances': instances})
        return self.kwargs

    def perform_create(self, serializer):
        is_survey = self.request.data.get('is_survey', False)
        fxf = serializer.save(is_survey=is_survey, is_deployed=True)
        if not fxf.project:
            fxf.from_project = False
        fxf.save()
        if fxf.project:
            if not fxf.is_survey:    
                org = fxf.project.organization
                fxf.logs.create(source=self.request.user, type=18, title="General",
                          organization=org,
                          project = fxf.project,
                          content_object=fxf,
                          extra_object=fxf.project,
                          description='{0} assigned new General form  {1} to {2} '.format(
                              self.request.user.get_full_name(),
                              fxf.xf.title,
                              fxf.project.name))
        else:
            org = fxf.site.project.organization

            fxf.logs.create(source=self.request.user, type=19, title="General",
                                              organization=org,
                                              project=fxf.site.project,
                                              site = fxf.site,
                                              content_object=fxf,
                                              extra_object=fxf.site,
                                              description='{0} assigned new General form  {1} to {2} '.format(
                                                  self.request.user.get_full_name(),
                                                  fxf.xf.title,
                                                  fxf.site.name
                                              ))


class FormDetailViewset(viewsets.ReadOnlyModelViewSet):
    queryset = FieldSightXF.objects.all()
    serializer_class = FSXFAllDetailSerializer
