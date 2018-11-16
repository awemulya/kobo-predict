from __future__ import unicode_literals
from rest_framework import serializers
from onadata.apps.userrole.models import UserRole
from onadata.apps.users.serializers import UserSerializer


class UserRoleSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    group = serializers.CharField()

    class Meta:
        model = UserRole
        exclude = ()


class MySiteRolesSerializer(serializers.ModelSerializer):
    site = serializers.SerializerMethodField()
    project = serializers.SerializerMethodField()

    class Meta:
        model = UserRole
        fields = ('site', 'project')

    def get_site(self, obj):
        site = obj.site
        site_type = 0
        site_type_level = ""
        region_id = ""
        try:
            site_type = site.type.id
            site_type_level = site.type.name
        except Exception as e:
            pass
        try:
            region_id = site.region.id
        except Exception as e:
            pass
        bp = [m.image.url for m in self.context['blue_prints'] if m.site == site]
        return {'id': site.id, 'phone': site.phone, 'name': site.name, 'description': site.public_desc,
                                  'address':site.address, 'lat': repr(site.latitude), 'lon': repr(site.longitude),
                                  'identifier':site.identifier, 'progress': 0, 'type_id':site_type,
                                  'type_label':site_type_level,
                                  'add_desc': site.additional_desc, 'blueprints':bp,
                'site_meta_attributes_ans': site.site_meta_attributes_ans, 'region':region_id   }

    def get_project(self, obj):
        project = obj.project
        return {'name': project.name, 'id': project.id, 'description': project.public_desc,
                                     'address':project.address, 'type_id':project.type.id,
                                     'type_label':project.type.name,'phone':project.phone, 'organization_name':project.organization.name,
                                     'organization_url':project.organization.logo.url,
                                     'lat': repr(project.latitude), 'lon': repr(project.longitude), 'cluster_sites':project.cluster_sites, 'site_meta_attributes':project.site_meta_attributes}



