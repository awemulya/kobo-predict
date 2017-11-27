from rest_framework import serializers

from onadata.apps.fsforms.models import InstanceStatusChanged, InstanceImages, FInstance
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import FSXFSerializer
from onadata.apps.logger.models.instance import Instance

class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstanceImages
        exclude = ("instance_status",)

class FInstanceSerializer(serializers.ModelSerializer):
    site_fxf = FSXFSerializer()
    project_fxf = FSXFSerializer()
    class Meta:
        model = FInstance
        exclude = ()

class InstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instance
        exclude = ()

class FInstanceResponcesSerializer(serializers.ModelSerializer):
    # site_fxf = FSXFSerializer()
    # project_fxf = FSXFSerializer()
    get_responces = serializers.ReadOnlyField()
    submitted_by_username = serializers.ReadOnlyField(source="submitted_by.username")
    # instance = InstanceSerializer()
    class Meta:
        model = FInstance
        exclude = ('submitted_by')


class InstanceStatusChangedSerializer(serializers.ModelSerializer):
    finstance = FInstanceSerializer(read_only=True)
    images = ImagesSerializer(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    old_status = serializers.SerializerMethodField()
    new_status = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = InstanceStatusChanged

    def get_old_status(self,obj):
        return obj.get_old_status_display()

    def get_new_status(self,obj):
        return obj.get_new_status_display()

    def get_date(self,obj):
        return obj.date.isoformat()