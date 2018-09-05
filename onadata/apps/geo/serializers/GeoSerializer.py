from __future__ import unicode_literals
import json
from rest_framework import serializers
from onadata.apps.geo.models import GeoLayer
from rest_framework.exceptions import ValidationError
from django.core.urlresolvers import reverse

class GeoLayerSerializer(serializers.ModelSerializer):
    geo_layer = serializers.SerializerMethodField(read_only=True)

    class Meta:
    	model = GeoLayer
        fields = ('id', 'title', 'geo_layer')


    def get_geo_layer(self, obj):
        return reverse('fieldsight:geo-json', kwargs={'pk': obj.id})
