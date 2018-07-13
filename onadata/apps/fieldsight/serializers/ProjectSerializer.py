from __future__ import unicode_literals
import json
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.fieldsight.models import Project, ProjectType, OrganizationType
from onadata.apps.fsforms.models import FieldSightXF


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
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    class Meta:
        model = Project
        read_only_fields = ('logo', 'location')
        exclude = ()

    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')), srid=4326)
        validated_data.update({'is_active': True, 'location': p})
        project = Project.objects.create(**validated_data)
        project.save()
        return project



class ProjectSerializer(serializers.ModelSerializer):
    latitude= serializers.CharField()
    longitude= serializers.CharField()
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    organization_label = serializers.ReadOnlyField(source='organization.name', read_only=True)

    class Meta:
        model = Project
        read_only_fields = ('logo', 'location', 'latitude', 'longitude')
        exclude = ()


    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')),srid=4326)
        validated_data.update({'location':p})
        project = Project.objects.create(**validated_data)
        return project

class ProjectMiniSerializer(serializers.ModelSerializer):
    site_meta_attributes = serializers.JSONField(binary=False)
    class Meta:
        model = Project
        fields = ('id', 'name', 'cluster_sites', 'site_meta_attributes',)

class ProjectMetasSerializer(serializers.ModelSerializer):
    site_meta_attributes = serializers.JSONField(binary=False)
    class Meta:
        model = Project
        fields = ('site_meta_attributes',)

class ProjectFormsSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField('get_title', read_only=True)
    json = serializers.SerializerMethodField('get_json', read_only=True)

    class Meta:
        model = FieldSightXF
        fields = ('id', 'title', 'json',)
    
    
    def get_title(self, obj):
        return u"%s" % obj.xf.title

    def get_json(self, obj):
        return json.loads(obj.xf.json)