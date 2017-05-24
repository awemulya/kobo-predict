from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from onadata.apps.users.models import UserProfile


def validateEmail( email ):
    from django.core.validators import validate_email
    try:
        validate_email( email )
        try:
            user = User.objects.get(email__iexact=email)
            return True
        except:
            raise ValidationError("Email not in use")
    except ValidationError:
        return False


class AuthCustomTokenSerializer(serializers.Serializer):
    email_or_username = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')

        if email_or_username and password:
            # Check if user sent email
            if validateEmail(email_or_username):
                user_request = get_object_or_404(
                    User,
                    email=email_or_username,
                )

                email_or_username = user_request.username

            user = authenticate(username=email_or_username, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise ValidationError(msg)
        else:
            msg = _('Must include "email or username" and "password"')
            raise ValidationError(msg)

        attrs['user'] = user
        return attrs


# class ProfileSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = UserProfile
#         exclude = ('user', 'id', 'organization')
#

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        exclude = ('last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions')
        write_only_fields = ('password',)

    def get_profile_picture(self, obj):
        try:
            if obj.user_profile.profile_picture:
                return obj.user_profile.profile_picture.url
        except:
            return None
        return None


class SearchableUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        exclude = ('is_superuser', 'is_staff', 'groups', 'user_permissions', 'password')

    def get_profile_picture(self, obj):
        try:
            if obj.user_profile.profile_picture:
                return obj.user_profile.profile_picture.url
        except:
            return None
        return None


# class ProfileUserSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = User
#         exclude = ('last_login', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'groups', 'user_permissions','password')
#         read_only_fields = ('username', 'email', 'last_login', 'date_joined', 'id')


class UserSerializerProfile(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")

    class Meta:
        model = UserProfile
        exclude = ('user',)
        read_only_fields = ('id', 'profile_picture')

    def update(self,  instance, validated_data):
        data = self.context['request'].data
        user_data = validated_data.pop("user")
        User.objects.filter(pk=instance.user.pk).update(**user_data)
        # profile_picture = data.get("profile_picture", False)
        # if profile_picture:
        #     validated_data.update({'profile_picture':profile_picture})
        UserProfile.objects.filter(pk=instance.pk).update(**validated_data)
        profile =  UserProfile.objects.get(pk=instance.pk)
        profile_picture = data.get("profile_picture", False)
        if profile_picture:
            profile.profile_picture = profile_picture
            profile.save()
        return profile


class UserDetailSerializer(serializers.ModelSerializer):
        profile_picture = serializers.SerializerMethodField()

        class Meta:
            model = User
            exclude = ('is_superuser', 'is_staff', 'groups', 'user_permissions',)

        def get_profile_picture(self, obj):
            if obj.user_profile.profile_picture:
                return obj.user_profile.profile_picture.url
            return None


