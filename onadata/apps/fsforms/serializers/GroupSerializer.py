from rest_framework import serializers

from onadata.apps.fsforms.models import FormGroup


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = FormGroup
        fields = ('id', 'name', 'description', 'creator')
        read_only_fields = ('creator',)

