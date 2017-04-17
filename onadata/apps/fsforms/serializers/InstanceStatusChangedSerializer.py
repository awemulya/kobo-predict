from rest_framework import serializers

from onadata.apps.fsforms.models import InstanceStatusChanged


class InstanceStatusChangedSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    old_status = serializers.SerializerMethodField()
    new_status = serializers.SerializerMethodField()

    class Meta:
        model = InstanceStatusChanged

    def get_old_status(self,obj):
        return obj.get_old_status_display()

    def get_new_status(self,obj):
        return obj.get_new_status_display()