from django.db.models import Q
from rest_framework import viewsets

from onadata.apps.fsforms.serializers.XformSerializer import XFormListSerializer
from onadata.apps.logger.models import XForm


class XFormViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing xforms.
    """
    queryset = XForm.objects.all()
    serializer_class = XFormListSerializer

    def get_queryset(self):
        return self.queryset.filter(Q(user=self.request.user) |
                Q(user__user_profile__organization=self.request.organization))
