from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from random import randint


class Serializer(GeoJSONSerializer):
    def get_dump_object(self, obj):
        data = super(Serializer, self).get_dump_object(obj)
        # Extend to your taste
        data.update(id=obj.pk)
        # data.update(status=4)
        # data.update(progress=obj.site_progress)
        return data