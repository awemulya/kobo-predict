from rest_framework import serializers

from onadata.apps.userrole.models import UserRole


class UserRoleSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    site = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ('username','email','group','site','project','organization')
        read_only_fields = ('username','email','group','site','project','organization')


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


