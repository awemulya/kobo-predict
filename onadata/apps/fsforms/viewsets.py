
from django.conf import settings
from rest_framework import serializers
from rest_framework.response import Response
from onadata.apps.api.viewsets.xform_list_api import XFormListApi
from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.fsforms.serializers import FSXFormListSerializer


# 10,000,000 bytes
DEFAULT_CONTENT_LENGTH = getattr(settings, 'DEFAULT_CONTENT_LENGTH', 10000000)


class AssignedXFormListApi(XFormListApi):
    serializer_class = FSXFormListSerializer
    queryset = FieldSightXF.objects.filter(xf__downloadable=True)
    template_name = 'fsforms/assignedFormList.xml'

    def filter_queryset(self, queryset):
        site_id = self.kwargs.get('site_id', None)
        if site_id is None:
            # If no username is specified, the request must be authenticated
            if self.request.user.is_anonymous():
                # raises a permission denied exception, forces authentication
                self.permission_denied(self.request)
            else:
                try:
                    int(site_id)
                except:
                    raise serializers.ValidationError({'site': "Site Id Not Given."})
                else:
                    return super(AssignedXFormListApi, self).filter_queryset(queryset)

                return super(AssignedXFormListApi, self).filter_queryset(queryset)
        site_id = int(site_id)
        queryset = queryset.filter(site__id=site_id)
        return queryset

    def list(self, request, *args, **kwargs):
        self.object_list = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data, headers=self.get_openrosa_headers())



