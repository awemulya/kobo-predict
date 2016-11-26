from rest_framework import viewsets

from onadata.apps.fieldsight.models import ProjectType, Project
from onadata.apps.fieldsight.serializers.ProjectSerializer import ProjectTypeSerializer, ProjectSerializer


class ProjectTypeViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing project and site  type.
    """
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
