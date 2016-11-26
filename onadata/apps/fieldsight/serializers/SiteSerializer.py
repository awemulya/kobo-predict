from rest_framework import serializers

from onadata.apps.fieldsight.models import Site


class SiteSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_site_type', read_only=True)
    project_label = serializers.CharField(source='get_project_name', read_only=True)
    organization_label = serializers.CharField(source='get_organization_name', read_only=True)

    class Meta:
        model = Site
        exclude = ()