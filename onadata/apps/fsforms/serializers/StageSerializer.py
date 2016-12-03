from rest_framework import serializers

from onadata.apps.fsforms.models import Stage
from onadata.apps.fsforms.serializers.GroupSerializer import GroupSerializer


class StageSerializer(serializers.ModelSerializer):
    main_stage = serializers.ReadOnlyField(source='stage.name', read_only=True)

    class Meta:
        model = Stage
        fields = ('name', 'description', 'id', 'stage', 'main_stage', 'order')

