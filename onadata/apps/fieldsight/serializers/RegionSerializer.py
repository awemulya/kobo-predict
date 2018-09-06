from __future__ import unicode_literals
from rest_framework import serializers

from onadata.apps.fieldsight.models import Region


class RegionSerializer(serializers.ModelSerializer):
    total_sites_count = serializers.SerializerMethodField('get_sites_count', read_only=True)

    def get_sites_count(self, obj):
        return obj.get_sites_count()

    class Meta:
        model = Region
        fields = ('id', 'name', 'identifier', 'total_sites_count', 'parent')

class AllMainRegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ('id', 'name', 'identifier',)

