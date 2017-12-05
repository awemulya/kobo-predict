from rest_framework import serializers
from rest_framework.reverse import reverse

from onadata.apps.fsforms.models import FieldSightXF, EducationalImages, EducationMaterial
from onadata.apps.logger.models import XForm
from onadata.libs.utils.decorators import check_obj


# class FSXFormSerializer(serializers.HyperlinkedModelSerializer):
#     formid = serializers.ReadOnlyField(source='id')
#     metadata = serializers.SerializerMethodField('get_xform_metadata')
#     owner = serializers.HyperlinkedRelatedField(view_name='user-detail',
#                                                 source='user',
#                                                 lookup_field='username',
#                                                 queryset=User.objects.all())
#     public = BooleanField(source='shared')
#     public_data = BooleanField(source='shared_data')
#     require_auth = BooleanField()
#     submission_count_for_today = serializers.ReadOnlyField()
#     tags = TagListSerializer(read_only=True)
#     title = serializers.CharField(max_length=255)
#     url = serializers.HyperlinkedIdentityField(view_name='xform-detail',
#                                                lookup_field='pk')
#     users = serializers.SerializerMethodField('get_xform_permissions')
#     hash = serializers.SerializerMethodField()
#
#     @check_obj
#     def get_hash(self, obj):
#         return u"md5:%s" % obj.hash
#
#     # Tests are expecting this "public" to be passed only "True" or "False"
#     # and as a string. I don't know how it worked pre-migrations to django 1.8
#     # but now it must be implemented manually
#     def validate(self, attrs):
#         shared = attrs.get('shared')
#         if shared not in (None, 'True', 'False'):
#             msg = "'%s' value must be either True or False." % shared
#             raise serializers.ValidationError({'shared': msg})
#         attrs['shared'] = shared == 'True'
#         return attrs
#
#     class Meta:
#         model = XForm
#         read_only_fields = (
#             'json', 'xml', 'date_created', 'date_modified', 'encrypted',
#             'bamboo_dataset', 'last_submission_time')
#         exclude = ('json', 'xml', 'xls', 'user',
#                    'has_start_time', 'shared', 'shared_data')
#
#     # Again, this is to match unit tests
#     @property
#     def data(self):
#         data = super(XFormSerializer, self).data
#         if 'num_of_submissions' in data and data['num_of_submissions'] is None:
#             data['num_of_submissions'] = 0
#         return data
#
#     def get_xform_permissions(self, obj):
#         return get_object_users_with_permissions(obj, serializable=True)
#
#     def get_xform_metadata(self, obj):
#         if obj:
#             return MetaDataSerializer(obj.metadata_set.all(),
#                                       many=True, context=self.context).data
#
#         return []

class FSXFormListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_title', read_only=True)
    descriptionText = serializers.SerializerMethodField('get_description', read_only=True)
    site_name = serializers.ReadOnlyField()
    majorMinorVersion = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()
    downloadUrl = serializers.SerializerMethodField('get_url', read_only=True)
    formID = serializers.SerializerMethodField('get_form_id', read_only=True)
    manifestUrl = serializers.SerializerMethodField('get_manifest_url')

    class Meta:
        model = FieldSightXF
        fields = ('id', 'site_name', 'site','is_staged', 'is_scheduled', 'is_survey', 'downloadUrl', 'manifestUrl',
                  'name', 'descriptionText','formID', 'majorMinorVersion','version', 'hash')

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
        site_id = obj.site.id if obj.site else 0
        kwargs = {'pk': obj.pk, 'site_id': site_id}
        request = self.context.get('request')

        return reverse('forms:manifest-url', kwargs=kwargs, request=request)


class EMImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalImages
        exclude = ("educational_material",)


class EMSerializer(serializers.ModelSerializer):
    em_images = EMImagesSerializer(many=True, read_only=True)
    class Meta:
        model = EducationMaterial
        exclude = ('stage',)

class FSXFormSerializer(serializers.ModelSerializer):
    em = EMSerializer(read_only=True)
    name = serializers.SerializerMethodField('get_title', read_only=True)
    id_string = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()

    def validate(self, data):
        """
        Check that form is unique for general form.
        """
        if data.has_key('site'):
            if FieldSightXF.objects.filter(
                    xf=data['xf'], is_staged=False, is_scheduled=False, site=data['site']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate General Forms Not Allowded")
        elif data.has_key('project'):
            if FieldSightXF.objects.filter(
                    xf=data['xf'], is_staged=False, is_scheduled=False, project=data['project']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate General Forms Not Allowded")
        return data

    class Meta:
        model = FieldSightXF
        exclude = ()

    @check_obj
    def get_title(self, obj):
        return u"%s" % obj.xf.title

    @check_obj
    def get_id_string(self, obj):
        return u"%s" % obj.xf.id_string

    def get_responses_count(self, obj):
        is_project = self.context.get('is_project', False)
        if not is_project:
            return 0
        # pk = self.context['pk']
        if obj.is_survey or is_project == "1":
            return obj.project_form_instances.count()
        else:
            return obj.site_form_instances.count()


class XformSerializer(serializers.ModelSerializer):
    class Meta:
        model = XForm
        fields = ('title', 'id', 'id_string')


class FSXFSerializer(serializers.ModelSerializer):
    xf = XformSerializer()
    class Meta:
        model = FieldSightXF
        fields = ('xf','id',)