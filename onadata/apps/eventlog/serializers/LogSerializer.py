from django.contrib.gis.geos import Point
from rest_framework import serializers
from onadata.apps.evevtlog.models import FieldSightLog

class LogSerializer(serializers.ModelSerializer):
    source_img = serializers.ReadOnlyField(source='user.user_profile.profile_picture.url', read_only=True)
    source_url = serializers.SerializerMethodField('get_source_url', read_only=True)
    action_url = serializers.SerializerMethodField('get_event_url', read_only=True)
    
    class Meta:
        model = FieldSightLog
        exclude = (,)