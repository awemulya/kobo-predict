from rest_framework import viewsets
from rest_framework import serializers

from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.fsforms.serializers.FieldSightXFormApiSerializer import FSXFormListSerializer


class SiteFormViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing site forms.
    """
    queryset = FieldSightXF.objects.all()
    serializer_class = FSXFormListSerializer

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
                    return super(SiteFormViewSet, self).filter_queryset(queryset)

                return super(SiteFormViewSet, self).filter_queryset(queryset)
        site_id = int(site_id)
        queryset = queryset.filter(site__id=site_id)
        return queryset