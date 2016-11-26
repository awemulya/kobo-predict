from rest_framework import viewsets

from onadata.apps.fieldsight.models import OrganizationType, Organization
from onadata.apps.fieldsight.serializers.OrganizationSerializer import OrganizationTypeSerializer, OrganizationSerializer


class OrganizationTypeViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing organization type.
    """
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
