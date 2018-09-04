from __future__ import unicode_literals
import json
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.fieldsight.models import Project, ProjectType, OrganizationType
from onadata.apps.fsforms.models import FieldSightXF
from django.core.urlresolvers import reverse


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
        p = Point(round(float(validated_data.pop('longitude')), 6), round(float(validated_data.pop('latitude')), 6), srid=4326)
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
        p = Point(round(float(validated_data.pop('longitude')), 6), round(float(validated_data.pop('latitude')), 6), srid=4326)
        validated_data.update({'location':p})
        project = Project.objects.create(**validated_data)
        return project

class ProjectMiniSerializer(serializers.ModelSerializer):
    site_meta_attributes = serializers.JSONField(binary=False)
    class Meta:
        model = Project
        fields = ('id', 'name', 'cluster_sites', 'site_meta_attributes',)

class ProjectMinimalSerializer(serializers.ModelSerializer):
    label = serializers.ReadOnlyField(source='name', read_only=True)
    class Meta:
        model = Project
        fields = ('id', 'label', 'cluster_sites',)


class ProjectMetasSerializer(serializers.ModelSerializer):
    site_meta_attributes = serializers.JSONField(binary=False)
    class Meta:
        model = Project
        fields = ('site_meta_attributes',)

class ProjectFormsSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    json = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FieldSightXF
        fields = ('id', 'name', 'json',)
    
    
    def get_name(self, obj):
        return u"%s" % obj.xf.title

    def get_json(self, obj):
        return json.loads(obj.xf.json)


class ProjectMapDataSerializer(serializers.ModelSerializer):
    geojson_file = serializers.SerializerMethodField(read_only=True)
    updated_geojson = serializers.SerializerMethodField(read_only=True)
    geo_layers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FieldSightXF
        fields = ('id', 'name',)
    
    
    def get_geojson_file(self, obj):
        try:
            url = obj.project_geojson.geoJSON.url
        except:
            url = None
        return url

    def get_updated_geojson(self, obj):
        return reverse('fieldsight:ProjectSiteListGeoJSON', kwargs={'pk': obj.id})

    def get_geo_layers(self, obj):
        layers = obj.geo_layers.all()
        geo_layers = []
        for layer in layers:
            geo_layer = {}
            geo_layer['id'] = layer.id
            geo_layer['title'] = layer.title
            geo_layer['level'] = layer.level
            geo_layer['url'] = layer.geo_shape_file.url
            geo_layers.append(geo_layer)
        
        return geo_layers


