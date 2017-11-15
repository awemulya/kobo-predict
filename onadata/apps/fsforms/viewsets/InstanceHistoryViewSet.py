from rest_framework import viewsets

from onadata.apps.fsforms.models import InstanceStatusChanged, FInstance
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import InstanceStatusChangedSerializer, FInstanceResponcesSerializer
from rest_framework.pagination import PageNumberPagination
from onadata.apps.fsforms.models import FieldSightXF
from django.http import Http404


class InstanceHistoryViewSet(viewsets.ModelViewSet):
    queryset = InstanceStatusChanged.objects.all()
    serializer_class = InstanceStatusChangedSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(finstance__instance__id=self.kwargs.get('pk', None))



class InstanceHistoryDetailViewSet(viewsets.ModelViewSet):
    queryset = InstanceStatusChanged.objects.all()
    serializer_class = InstanceStatusChangedSerializer


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20

class InstanceResponseViewSet(viewsets.ModelViewSet):
    queryset = FInstance.objects.all()
    serializer_class = FInstanceResponcesSerializer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    pagination_class = LargeResultsSetPagination

    def filter_queryset(self, queryset):
        try:
            fsfom=FieldSightXF.objects.get(pk=self.kwargs.get('pk'))
        except FieldSightXF.DoesNotExist:
            raise Http404("No MyModel matches the given query.")
        if fsform.poject is not None:
            return queryset.filter(project_fxf_id = self.kwargs.get('pk'))     
        return queryset.filter(site_fxf_id = self.kwargs.get('pk')) 

