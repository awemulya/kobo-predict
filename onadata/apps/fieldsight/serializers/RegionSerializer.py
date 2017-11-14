from rest_framework import serializers

from onadata.apps.fieldsight.models import Region

class RegionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Region
        fields = ('id', 'name')
