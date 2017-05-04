from django.contrib.gis.geos import Point
from rest_framework import serializers

from onadata.apps.fieldsight.models import Project, ProjectType


class ProjectTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectType
        fields = ('id', 'name')


class ProjectSerializer(serializers.ModelSerializer):
    latitude= serializers.CharField()
    longitude= serializers.CharField()

    class Meta:
        model = Project
        exclude = ()
        read_only_fields = ('logo', 'location')

    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')),srid=4326)
        validated_data.update({'location':p})
        project = Project.objects.create(**validated_data)
        return project