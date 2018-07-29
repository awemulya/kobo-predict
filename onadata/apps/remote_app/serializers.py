import json
from rest_framework import serializers
from onadata.apps.fieldsight.models import Site


class SiteSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Site
        fields = ('id', 'identifier', 'name', 'location',
                  'attributes')

    def get_attributes(self, site):
        return site.site_meta_attributes_ans

    def get_location(self, site):
        return site.location and site.location.coords
