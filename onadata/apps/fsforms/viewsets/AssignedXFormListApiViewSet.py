from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from django.db.models import Q

from onadata.apps.fieldsight.models import Site
# from onadata.apps.main.models.meta_data import MetaData
from onadata.apps.api.viewsets.xform_list_api import XFormListApi
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFormListSerializer
from onadata.apps.fsforms.serializers.FieldSightXformManifestSerializer import FSXFormManifestSerializer


class AssignedXFormListApi(XFormListApi):
    serializer_class = FSXFormListSerializer
    queryset = FieldSightXF.objects.all()
    template_name = 'fsforms/assignedFormList.xml'

    def filter_queryset(self, queryset):
        if self.request.user.is_anonymous():
            self.permission_denied(self.request)
        site_id = self.kwargs.get('site_id', None)
        queryset = queryset.filter(site__id=site_id, site__isnull=False, is_deployed=True)
        return queryset

    @detail_route(methods=['GET'])
    def manifest(self, request, *args, **kwargs):
        if kwargs.get('site_id') == '0':
            self.object = FieldSightXF.objects.get(pk=kwargs.get('pk'))
        else:
            self.object = self.get_object()
        object_list = []
        context = self.get_serializer_context()
        serializer = FSXFormManifestSerializer(object_list, many=True,
                                             context=context)

        return Response(serializer.data, headers=self.get_openrosa_headers())

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data, headers=self.get_openrosa_headers())

    def project_forms(self, request, *args, **kwargs):
        self.object_list = self.queryset.filter(Q(project__id=kwargs.get('project_id'), site__isnull=True,
                                                  is_deployed=True, is_deleted=False) |
                                                Q(project__id=kwargs.get('project_id'), site__isnull=True,
                                                  is_survey=True, is_deleted=False))

        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data, headers=self.get_openrosa_headers())

    def site_overide_forms(self, request, *args, **kwargs):
        self.object_list = self.queryset.filter(site__project_id=kwargs.get('project_id'), from_project=False, is_deployed=True, is_deleted=False)

        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data, headers=self.get_openrosa_headers())


