from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.fieldsight.models import Site, SiteCreateSurveyImages, ProjectType


class SiteSerializer(serializers.ModelSerializer):
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    prog = serializers.SerializerMethodField('get_progress', read_only=True)
    blueprints = serializers.SerializerMethodField('get_blue_prints', read_only=True)
    organization_label = serializers.ReadOnlyField(source='project.organization.name', read_only=True)

    class Meta:
        model = Site
        exclude = ('project','is_active','type',)

    def get_progress(self, obj):
        return obj.progress()

    def get_blue_prints(self, obj):
        data = obj.blueprints.all()
        return [m.image.url for m in data]


class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteCreateSurveyImages
        read_only_fields = ("site",)


class ProjectTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectType
        read_only_fields = ("id",)


class SiteCreationSurveySerializer(serializers.ModelSerializer):
    images = PhotoSerializer(many=True, read_only=True)
    latitude= serializers.CharField()
    longitude= serializers.CharField()

    class Meta:
        model = Site
        read_only_fields = ('logo', 'location')

    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')),srid=4326)
        validated_data.update({'is_survey': True,'location':p})
        site=Site.objects.create(**validated_data)
        image = self.context['request'].FILES.values()
        for img in image:
            SiteCreateSurveyImages.objects.create(image=img, site=site)
        return site


class SiteReviewSerializer(serializers.ModelSerializer):
    images = PhotoSerializer(many=True, read_only=True)
    type = ProjectTypeSerializer()
    latitude= serializers.CharField()
    longitude= serializers.CharField()

    class Meta:
        model = Site
        read_only_fields = ('logo', 'location', 'type')

    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')),srid=4326)
        validated_data.update({'is_survey': True,'location':p})
        site=Site.objects.create(**validated_data)
        image = self.context['request'].FILES.values()
        for img in image:
            SiteCreateSurveyImages.objects.create(image=img, site=site)
        return site


