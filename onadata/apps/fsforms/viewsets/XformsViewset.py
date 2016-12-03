from rest_framework import viewsets

from onadata.apps.fsforms.serializers.XformSerializer import XFormListSerializer
from onadata.apps.logger.models import XForm


class XFormViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing xforms.
    """
    queryset = XForm.objects.all()
    serializer_class = XFormListSerializer
