from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, ProjectType


class ProjectTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectType
        fields = ('id', 'name')


class ProjectSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_project_type', read_only=True)
    organization_label = serializers.CharField(source='get_organization_name', read_only=True)

    class Meta:
        model = Project
        exclude = ()