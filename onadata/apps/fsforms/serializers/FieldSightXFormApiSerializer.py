from rest_framework import serializers
from rest_framework.reverse import reverse

from onadata.apps.fsforms.models import FieldSightXF
from onadata.libs.utils.decorators import check_obj


class FSXFormListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_title', read_only=True)
    descriptionText = serializers.SerializerMethodField('get_description', read_only=True)

    class Meta:
        model = FieldSightXF
        fields = ('id', 'name', 'descriptionText', 'is_staged', 'is_scheduled')

    def get_version(self, obj):
        return None

    def get_majorMinorVersion(self, obj):
        return None

    @check_obj
    def get_hash(self, obj):
        return u"md5:%s" % obj.xf.hash

    @check_obj
    def get_title(self, obj):
        return u"%s" % obj.xf.title

    @check_obj
    def get_form_id(self, obj):
        return u"%s" % obj.xf.id_string

    @check_obj
    def get_description(self, obj):
        return u"%s" % obj.xf.description

    @check_obj
    def get_url(self, obj):
        kwargs = {'pk': obj.pk}
        request = self.context.get('request')

        return reverse('forms:download_xform', kwargs=kwargs, request=request)

    @check_obj
    def get_manifest_url(self, obj):
        kwargs = {'pk': obj.pk, 'site_id':obj.site.id}
        request = self.context.get('request')

        return reverse('forms:manifest-url', kwargs=kwargs, request=request)
