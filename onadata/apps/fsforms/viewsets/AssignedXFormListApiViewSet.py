from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from onadata.apps.main.models.meta_data import MetaData
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
        site_id = int(site_id)
        queryset = queryset.filter(site__id=site_id, is_deployed=True)
        return queryset

    @detail_route(methods=['GET'])
    def manifest(self, request, *args, **kwargs):
        self.object = self.get_object()
        object_list = MetaData.objects.filter(data_type='media',
                                              xform=self.object.xf)
        context = self.get_serializer_context()
        serializer = FSXFormManifestSerializer(object_list, many=True,
                                             context=context)

        return Response(serializer.data, headers=self.get_openrosa_headers())

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data, headers=self.get_openrosa_headers())
