from rest_framework import viewsets

from onadata.apps.fsforms.models import FormGroup
from onadata.apps.fsforms.serializers.GroupSerializer import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing Form Groups.
    """
    queryset = FormGroup.objects.all()
    serializer_class = GroupSerializer
