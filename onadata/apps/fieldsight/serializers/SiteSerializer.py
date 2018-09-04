from __future__ import unicode_literals
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.fieldsight.models import Site, Region, SiteCreateSurveyImages, ProjectType, Project, SiteType


class SiteSerializer(serializers.ModelSerializer):
    type_label = serializers.ReadOnlyField(source='type.name', read_only=True)
    prog = serializers.SerializerMethodField('get_progress', read_only=True)
    blueprints = serializers.SerializerMethodField('get_blue_prints', read_only=True)
    organization_label = serializers.ReadOnlyField(source='project.organization.name', read_only=True)
    get_site_submission_count = serializers.ReadOnlyField()
    # submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Site
        exclude = ('project','type',)
        read_only_fields = ('is_active',)

    def get_progress(self, obj):
        stages = obj.site_forms.filter(xf__isnull=False, is_staged=True, is_deleted=False).count()
        approved = obj.site_instances.filter(form_status=3, site_fxf__is_staged=True).count()
        if not approved:
            return 0
        if not stages:
            return 0
        p = ("%.0f" % (approved/(stages*0.01)))
        p = int(p)
        if p > 99:
            return 100
        return p
        # return obj.progress()

    def get_blue_prints(self, obj):
        data = obj.blueprints.all()
        return [m.image.url for m in data]

    def get_submission_count(self, obj):
        instances = obj.site_instances.all()
        outstanding, flagged, approved, rejected = 0, 0, 0, 0
        for submission in instances:
            if submission.form_status == 0:
                outstanding += 1
            elif submission.form_status == 1:
                rejected += 1
            elif submission.form_status == 2:
                flagged += 1
            elif submission.form_status == 3:
                approved += 1
        response = {}
        response['outstanding'] = outstanding
        response['rejected'] = rejected
        response['flagged'] = flagged
        response['approved'] = approved
        return response



class SiteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        exclude = ('project',)
        read_only_fields = ('is_active',)

    def update(self, instance, validated_data):
        lat = self.context['request'].data.get('latitude', False)
        long = self.context['request'].data.get('longitude', False)
        type_id = self.context['request'].data.get('type', False)
        site = super(SiteUpdateSerializer, self).update(instance, validated_data)
        if lat and long:
            lat = float(lat)
            long = float(long)
            location = Point(round(lat, 6), round(long, 6), srid=4326)
            site.location = location
        if type_id:
            site.type = SiteType.objects.get(pk=type_id)
        site.save()
        return site


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        exclude = ('organization',)

class PhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteCreateSurveyImages
        read_only_fields = ("site",)


class ProjectTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectType
        read_only_fields = ("id",)

class SiteTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiteType
        read_only_fields = ("id",)


class SiteCreationSurveySerializer(serializers.ModelSerializer):
    images = PhotoSerializer(many=True, read_only=True)
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    class Meta:
        model = Site
        read_only_fields = ('logo', 'location')
        exclude = ('current_progress', 'current_status')

    def create(self, validated_data):
        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')),srid=4326)
        validated_data.update({'is_survey': False,'is_active':True,'location':p,})
        site = Site.objects.create(**validated_data)
        image = self.context['request'].FILES.values()
        for img in image:
            SiteCreateSurveyImages.objects.create(image=img, site=site)
        return site


class SiteReviewSerializer(serializers.ModelSerializer):
    create_surveys = PhotoSerializer(many=True, read_only=True)
    type = ProjectTypeSerializer(read_only=True)
    latitude = serializers.CharField()
    longitude = serializers.CharField()

    class Meta:
        model = Site
        read_only_fields = ('logo', 'location', 'create_surveys','project')

    def update(self, instance, validated_data):
        data = self.context['request'].data
        type_id = data.pop('type')
        site_type = ProjectType.objects.get(pk=type_id)
        verify_survey = data.pop('is_survey')
        if verify_survey:
            validated_data.update({'is_survey': False})
            validated_data.update({'is_active': True})
        else:
            validated_data.update({'is_survey': True})
            validated_data.update({'is_active': False})

        p = Point(float(validated_data.pop('longitude')), float(validated_data.pop('latitude')), srid=4326)
        validated_data.update({'location':p})
        Site.objects.filter(pk=instance.pk).update(**validated_data)
        site = Site.objects.get(pk=instance.id)
        site.type = site_type
        site.save()
        return site


class MinimalSiteSerializer(serializers.ModelSerializer):
    region = serializers.ReadOnlyField(source='region.identifier', read_only=True)

    class Meta:
        model = Site
        fields = ('id','name', 'identifier','type','region', )
        read_only_fields = ('is_active',)


class SuperMinimalSiteSerializer(serializers.ModelSerializer):
    label = serializers.ReadOnlyField(source='name', read_only=True)

    class Meta:
        model = Site
        fields = ('id','label', 'identifier',)

class RegionSerializer(serializers.ModelSerializer):
    get_sites_count = serializers.ReadOnlyField()

    class Meta:
        model = Region
        fields = ('id','name', 'identifier', 'parent')

class RegionSerializer(serializers.ModelSerializer):
    get_sites_count = serializers.ReadOnlyField()

    class Meta:
        model = Region
        fields = ('id','name', 'identifier', 'get_sites_count', 'parent')
