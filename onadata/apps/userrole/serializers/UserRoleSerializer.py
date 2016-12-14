from rest_framework import serializers

from onadata.apps.userrole.models import UserRole


class UserRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserRole
        fields = ('id', 'user', 'group', 'site',
                  'project', 'organization')
