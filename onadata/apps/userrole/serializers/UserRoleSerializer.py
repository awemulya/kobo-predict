from rest_framework import serializers
from onadata.apps.userrole.models import UserRole


class UserRoleSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    skype = serializers.SerializerMethodField()
    profile_picture = serializers.SerializerMethodField()


    class Meta:
        model = UserRole
        fields = ('username','email','address','gender','phone','skype','group','site','project','organization','profile_picture')
        read_only_fields = ('username','email','address','gender','phone','skype','group','site','project','organization','profile_picture')


    def get_username(self,obj):
        return obj.user.username

    def get_email(self,obj):
        return obj.user.email

    def get_group(self,obj):
        return obj.group.name



    def get_site(self,obj):
        if obj.site:
            return obj.site.name

    def get_project(self,obj):
        if obj.project:
            return obj.project.name

    def get_organization(self,obj):
        if obj.organization:
            return obj.organization.name
    # def get_address(self,obj):
    #     if obj.user:
    #         if UserProfile.objects.filter(user=obj.user).exists():
    #             user_profile = UserProfile.objects.get(user=obj.user)
    #             if user_profile:
    #                 return user_profile.address
    #     return None

    def get_address(self,obj):
        if obj.user.user_profile:
            return obj.user.user_profile.address
        return None
    def get_gender(self,obj):
        if obj.user.user_profile:
            return obj.user.user_profile.gender
        return None
    def get_phone(self,obj):
        if obj.user.user_profile:
            return obj.user.user_profile.phone
        return None
    def get_skype(self,obj):
        if obj.user.user_profile:
            return obj.user.user_profile.skype
        return None
    def get_profile_picture(self,obj):
        if obj.user.user_profile.profile_picture:
            return obj.user.user_profile.profile_picture.url
        return None


