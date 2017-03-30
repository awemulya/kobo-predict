from rest_framework import serializers
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.serializers import UserSerializer


class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    profile_picture = serializers.SerializerMethodField()
    group = serializers.CharField()

    class Meta:
        model = UserRole
        exclude = ()

    def get_profile_picture(self, obj):
        if obj.user.user_profile.profile_picture:
            return obj.user.user_profile.profile_picture.url
        return None


