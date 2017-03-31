from rest_framework import serializers
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.serializers import UserSerializer


class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    group = serializers.CharField()

    class Meta:
        model = UserRole
        exclude = ()



