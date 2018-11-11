import json
from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.eventlog.models import FieldSightLog, CeleryTaskProgress

class LogSerializer(serializers.ModelSerializer):
    source_uid = serializers.ReadOnlyField(source='source_id', read_only=True)
    source_name = serializers.SerializerMethodField(read_only=True)
    source_img = serializers.ReadOnlyField(source='source.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    
    get_event_name = serializers.ReadOnlyField()
    get_event_url = serializers.ReadOnlyField()

    get_extraobj_name = serializers.ReadOnlyField()
    get_extraobj_url = serializers.ReadOnlyField()

    get_absolute_url = serializers.ReadOnlyField()

    extra_json = serializers.JSONField(binary=False)
    
    # org_name = serializers.ReadOnlyField(source='organization.name', read_only=True)
    # get_org_url = serializers.ReadOnlyField()

    # project_name = serializers.ReadOnlyField(source='project.name', read_only=True)
    # get_project_url = serializers.ReadOnlyField()

    # site_name = serializers.ReadOnlyField(source='site.name', read_only=True)
    # get_site_url = serializers.ReadOnlyField()

    class Meta:
        model = FieldSightLog
        exclude = ('description', 'is_seen', 'content_type', 'organization', 'project', 'site', 'object_id', 'extra_object_id', 'source', 'extra_content_type',)

    def get_source_name(self, obj):
        return obj.source.first_name + " " + obj.source.last_name


class NotificationSerializer(serializers.ModelSerializer):
    source_uid = serializers.ReadOnlyField(source='source_id', read_only=True)
    source_name = serializers.SerializerMethodField(read_only=True)
    source_img = serializers.ReadOnlyField(source='source.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    
    get_event_name = serializers.ReadOnlyField()
    get_event_url = serializers.ReadOnlyField()

    get_extraobj_name = serializers.ReadOnlyField()
    get_extraobj_url = serializers.ReadOnlyField()

    get_absolute_url = serializers.ReadOnlyField()
    extra_json = serializers.JSONField(binary=False)
    # org_name = serializers.ReadOnlyField(source='organization.name', read_only=True)
    # get_org_url = serializers.ReadOnlyField()

    # project_name = serializers.ReadOnlyField(source='project.name', read_only=True)
    # get_project_url = serializers.ReadOnlyField()

    # site_name = serializers.ReadOnlyField(source='site.name', read_only=True)
    # get_site_url = serializers.ReadOnlyField()

    class Meta:
        model = FieldSightLog
        exclude = ('description', 'is_seen', 'content_type', 'organization', 'project', 'site', 'object_id', 'extra_object_id', 'source', 'extra_content_type',)

    def get_source_name(self, obj):
        return obj.source.first_name + " " + obj.source.last_name


class TaskSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField(read_only=True)
    source_img = serializers.ReadOnlyField(source='user.user_profile.profile_picture.url', read_only=True)
    get_source_url = serializers.ReadOnlyField()
    get_task_type_display = serializers.ReadOnlyField()
    get_event_name = serializers.ReadOnlyField()
    get_event_url = serializers.ReadOnlyField()


    class Meta:
        model = CeleryTaskProgress
        exclude = ('content_type', 'object_id', 'user', 'description')

    def get_source_name(self, obj):
        return obj.user.first_name + " " + obj.user.last_name
        
