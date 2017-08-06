from rest_framework import viewsets

from onadata.apps.fsforms.models import InstanceStatusChanged
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import InstanceStatusChangedSerializer


class InstanceHistoryViewSet(viewsets.ModelViewSet):
    queryset = InstanceStatusChanged.objects.all()
    serializer_class = InstanceStatusChangedSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(finstance__instance__id=self.kwargs.get('pk', None))



class InstanceHistoryDetailViewSet(viewsets.ModelViewSet):
    queryset = InstanceStatusChanged.objects.all()
    serializer_class = InstanceStatusChangedSerializer



