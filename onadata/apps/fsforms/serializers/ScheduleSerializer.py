from __future__ import unicode_literals
from rest_framework import serializers

from onadata.apps.fsforms.models import Schedule, Days, FieldSightXF, EducationMaterial
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer
from onadata.apps.fsforms.serializers.InstanceStatusChangedSerializer import FInstanceResponcesSerializer


class DaysSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Days
        exclude = ('index', 'selected')

    def get_selected(self, obj):
        return False


class ScheduleSerializer(serializers.ModelSerializer):
    em = serializers.SerializerMethodField('get_education_material', read_only=True)
    days = serializers.SerializerMethodField('get_all_days', read_only=True)
    form = serializers.SerializerMethodField('get_assigned_form', read_only=True)
    project_form = serializers.SerializerMethodField('get_assigned_project_form', read_only=True)
    xf = serializers.CharField()
    form_name = serializers.SerializerMethodField('get_assigned_form_name', read_only=True)
    id_string = serializers.SerializerMethodField()
    is_deployed = serializers.SerializerMethodField('get_is_deployed_status', read_only=True)
    default_submission_status = serializers.SerializerMethodField()
    responses_count = serializers.SerializerMethodField()
    latest_submission = serializers.SerializerMethodField()
    schedule_level = serializers.SerializerMethodField('get_schedule_level_type', read_only=True)

    def validate(self, data):
        """
        Check that form is unique for general form.
        """
        if data.has_key('site'):
            if FieldSightXF.objects.filter(
                    xf__id=data['xf'], is_staged=False, is_scheduled=True, site=data['site']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate Forms Not Allowed")
        elif data.has_key('project'):
            if FieldSightXF.objects.filter(
                    xf__id=data['xf'], is_staged=False, is_scheduled=True, project=data['project']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate Forms Not Allowed")
        return data

    class Meta:
        model = Schedule
        exclude = ('date_created', 'shared_level')

    def get_all_days(self, obj):
        return u"%s" % (", ".join(day.day for day in obj.selected_days.all()))

    def get_schedule_level_type(self, obj):
        if obj.schedule_level == 2:
            return "Monthly"
        elif obj.schedule_level == 1:
            return "Weekly"
        else:
            return "daily"

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

    def get_responses_count(self, obj):
        try:
            fsxf = FieldSightXF.objects.get(schedule=obj)
            
            if fsxf.fsform is None:
                return fsxf.project_form_instances.count()
            else:
                return fsxf.site_form_instances.filter(site_id=self.context.get('pk')).count()

        except FieldSightXF.DoesNotExist:
            return 0

    
    def get_latest_submission(self, obj):
        try:
            fsxf = FieldSightXF.objects.get(schedule=obj)
            
            if fsxf.fsform is None:
                response = fsxf.project_form_instances.order_by('-id')[:1]
            else:
                response = fsxf.site_form_instances.filter(site_id=self.context.get('pk')).order_by('-id')[:1]
            serializer = FInstanceResponcesSerializer(instance=response, many=True)
            return serializer.data 

        except FieldSightXF.DoesNotExist:
            return 0

        