from rest_framework import serializers

from onadata.apps.fieldsight.models import Site


class SiteSerializer(serializers.ModelSerializer):
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    project_label = serializers.ReadOnlyField(source='project.name', read_only=True)
    organization_label = serializers.ReadOnlyField(source='project.organization.name', read_only=True)

    class Meta:
        model = Site
        exclude = ()