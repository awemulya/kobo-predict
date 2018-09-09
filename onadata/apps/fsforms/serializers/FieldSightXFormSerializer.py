from rest_framework import serializers
from rest_framework.reverse import reverse

from onadata.apps.fsforms.models import FieldSightXF, EducationalImages, EducationMaterial, Schedule, Stage
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FInstanceResponcesSerializer
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

class StageFormSerializer(serializers.ModelSerializer):
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
                  'name', 'descriptionText','formID', 'majorMinorVersion','version', 'hash', 'stage')

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
    submission_data = serializers.SerializerMethodField()

    def validate(self, data):
        """
        Check that form is unique for general form / survey forms in projects.
        """
        if data.has_key('site'):
            if FieldSightXF.objects.filter(
                    xf=data['xf'], is_staged=False, is_scheduled=False, site=data['site']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate General Forms Not Allowded")
            elif FieldSightXF.objects.filter(
                    xf=data['xf'], is_staged=False, is_scheduled=False, project=data['site'].project).exists():
                raise serializers.ValidationError("Form Already Exists In Project, Duplicate General Forms Not Allowded")
        elif data.has_key('project'):
            if FieldSightXF.objects.filter(
                    xf=data['xf'], is_staged=False, is_scheduled=False, project=data['project']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate General Forms Not Allowded")
        return data

    class Meta:
        model = FieldSightXF
        exclude = ('shared_level',  'date_modified', 'stage',  'schedule', 'is_survey', 'is_deleted', 'form_status', 'is_staged', 'is_scheduled',)

    @check_obj
    def get_title(self, obj):
        return u"%s" % obj.xf.title

    @check_obj
    def get_id_string(self, obj):
        return u"%s" % obj.xf.id_string

    def get_submission_data(self, obj):
        is_project = self.context.get('is_project', False)
        instances = self.context.get('instances', [])
        count = 0
        response = None
        data = dict(count=count, latest_submission={})
        if not is_project:
            return data
        if is_project =="1" or obj.is_survey:
            for i in instances:
                if i.project_fxf == obj:
                    count += 1
                    if response is None:
                        response = i
        if is_project == "0":
            for i in instances:
                if i.project_fxf == obj:
                    count += 1
                    if response is None:
                        response = i
                elif  i.site_fxf == obj:
                    count += 1
                    if response is None:
                        response = i
        latest_submission_data = {}
        if response:
            # latest_submission_data = FInstanceResponcesSerializer(instance=response).data
            latest_submission_data = dict(user=response.submitted_by.username, date=response.date)
        return dict(count=count, latest=latest_submission_data)


class XformSerializer(serializers.ModelSerializer):

    class Meta:
        model = XForm
        fields = ('title', 'id', 'id_string')


class FSXFSerializer(serializers.ModelSerializer):
    xf = XformSerializer()
    downloadUrl = serializers.SerializerMethodField('get_url', read_only=True)
    manifestUrl = serializers.SerializerMethodField('get_manifest_url')

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

    class Meta:
        model = FieldSightXF
        fields = ('xf','id', 'default_submission_status','downloadUrl', 'manifestUrl')


class ScheduleSerializerAllDetail(serializers.ModelSerializer):
    em = serializers.SerializerMethodField('get_education_material', read_only=True)
    days = serializers.SerializerMethodField('get_all_days', read_only=True)
    form = serializers.SerializerMethodField('get_assigned_form', read_only=True)
    project_form = serializers.SerializerMethodField('get_assigned_project_form', read_only=True)
    xf = serializers.CharField()
    form_name = serializers.SerializerMethodField('get_assigned_form_name', read_only=True)
    id_string = serializers.SerializerMethodField()
    is_deployed = serializers.SerializerMethodField('get_is_deployed_status', read_only=True)
    default_submission_status = serializers.SerializerMethodField()
    schedule_level = serializers.SerializerMethodField('get_schedule_level_type', read_only=True)

    class Meta:
        model = Schedule
        exclude = ('date_created', 'shared_level')

    def get_schedule_level_type(self, obj):
        if obj.schedule_level == 2:
            return "Monthly"
        elif obj.schedule_level == 1:
            return "Weekly"
        else:
            return "Daily"

    def get_all_days(self, obj):
        return u"%s" % (", ".join(day.day for day in obj.selected_days.all()))

    def get_assigned_form(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(schedule=obj)
            if fsxf.xf:
                return fsxf.id
        return None

    def get_assigned_form_name(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(schedule=obj)
            if fsxf.xf:
                return fsxf.xf.title
        return None

    def get_id_string(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(schedule=obj)
            if fsxf.xf:
                return fsxf.xf.id_string
        return None

    def get_assigned_project_form(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj, fsform__isnull=False).exists():
            return None
        else:
            fsxf = FieldSightXF.objects.get(schedule=obj, fsform__isnull=False)
            if fsxf.fsform:
                return fsxf.fsform.id
        return None

    def get_is_deployed_status(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj).exists():
            return False
        else:
            return FieldSightXF.objects.get(schedule=obj).is_deployed

    def get_default_submission_status(self, obj):
        if not FieldSightXF.objects.filter(schedule=obj).exists():
            return False
        else:
            return FieldSightXF.objects.get(schedule=obj).default_submission_status

    def get_education_material(self, obj):
        if not EducationMaterial.objects.filter(fsxf=obj.schedule_forms).exists():
            return {}
        em =  EducationMaterial.objects.get(fsxf=obj.schedule_forms)
        # em =  EducationMaterial.objects.first()
        return EMSerializer(em).data



class MainStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        exclude = ('shared_level',)


class SubStageSerializerAllDetail(serializers.ModelSerializer):
    em = EMSerializer(read_only=True)
    main_stage = serializers.SerializerMethodField()

    class Meta:
        model = Stage
        exclude = ('shared_level', 'site', 'group', 'ready', 'project','stage', 'date_modified', 'date_created',)

    def get_main_stage(self,obj):
        if not obj.stage:
            return {}
        return MainStageSerializer(obj.stage).data



class FSXFAllDetailSerializer(serializers.ModelSerializer):
    xf = XformSerializer()
    schedule = ScheduleSerializerAllDetail()
    stage = SubStageSerializerAllDetail()

    downloadUrl = serializers.SerializerMethodField('get_url', read_only=True)
    manifestUrl = serializers.SerializerMethodField('get_manifest_url')
    latest_submission = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()

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

    def get_latest_submission(self, obj):
        try:

            if obj.site is None or obj.is_survey:
                response = obj.project_form_instances.order_by('-id')[:1]
            else:
                response = obj.site_form_instances.all().order_by('-id')[:1]
            serializer = FInstanceResponcesSerializer(instance=response, many=True)
            return serializer.data

        except FieldSightXF.DoesNotExist:
            return 0

    def get_responses_count(self, obj):
        try:
            if obj.site is None or obj.is_survey:
                return obj.project_form_instances.count()
            else:
                return obj.site_form_instances.count()

        except FieldSightXF.DoesNotExist:
            return 0

    class Meta:
        model = FieldSightXF
        exclude = ()

