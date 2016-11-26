from rest_framework import serializers

from onadata.apps.fieldsight.models import OrganizationType, Organization


class OrganizationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationType
        fields = ('id', 'name')


class OrganizationSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source='get_organization_type', read_only=True)

    class Meta:
        model = Organization
        exclude = ()