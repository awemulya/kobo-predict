from __future__ import unicode_literals
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONSerializer
from random import randint


class Serializer(GeoJSONSerializer):
    def get_dump_object(self, obj):
        data = super(Serializer, self).get_dump_object(obj)
        # Extend to your taste
        data.update(id=obj.pk)
        data.update(project=obj.project.name)
        data.update(status=obj.current_status)
        data.update(progress=obj.current_progress)
        return data

# class FieldsightMapSerializer(GeoJSONSerializer):
#     def get_dump_object(self, obj):
#         data = super(FieldsightMapSerializer, self).get_dump_object(obj)
#         # Extend to your taste
#         data.update(id=obj.pk)
#         try:
#             status = obj.site_instances.order_by('-date').first().form_status
#         except:
#             status = 4
#         data.update(status=status)
#         data.update(progress=obj.site_progress)
#         return data