from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.fieldsight.models import Project, ProjectType


class ProjectTypeSerializer(serializers.ModelSerializer):
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    organization_label = serializers.ReadOnlyField(source='organization.name', read_only=True)
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    class Meta:
        model = Project
        read_only_fields = ('location', 'latitude', 'longitude')
        exclude = ()


class ProjectCreationSerializer(serializers.ModelSerializer):
    # images = PhotoSerializer(many=True, read_only=True)
    latitude= serializers.CharField()
    longitude= serializers.CharField()

    class Meta:
        model = Project
        read_only_fields = ('logo', 'location')
        exclude = ('organization',)


class ProjectSerializer(serializers.ModelSerializer):
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    organization_label = serializers.ReadOnlyField(source='organization.name', read_only=True)
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    class Meta:
        model = Project
        read_only_fields = ('location', 'latitude', 'longitude')
        exclude = ()

