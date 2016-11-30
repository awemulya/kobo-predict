from rest_framework import serializers

from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.GroupSerializer import GroupSerializer


class StageSerializer(serializers.ModelSerializer):

    group = GroupSerializer()

    class Meta:
        model = Stage
        exclude = ()

