from rest_framework import serializers

from onadata.apps.fsforms.models import Schedule, Days, FieldSightXF, EducationMaterial
from onadata.apps.fsforms.serializers.FieldSightXFormSerializer import EMSerializer


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
    is_deployed = serializers.SerializerMethodField('get_is_deployed_status', read_only=True)

    def validate(self, data):
        """
        Check that form is unique for general form.
        """
        if data.has_key('site'):
            if FieldSightXF.objects.filter(
                    xf__id=data['xf'], is_staged=False, is_scheduled=True, site=data['site']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate Forms Not Allowded")
        elif data.has_key('project'):
            if FieldSightXF.objects.filter(
                    xf__id=data['xf'], is_staged=False, is_scheduled=True, project=data['project']).exists():
                raise serializers.ValidationError("Form Already Exists, Duplicate Forms Not Allowded")
        return data

    class Meta:
        model = Schedule
        exclude = ('date_created', 'shared_level')

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

    def get_education_material(self, obj):
        if not EducationMaterial.objects.filter(fsxf=obj.schedule_forms).exists():
            return {}
        em =  EducationMaterial.objects.get(fsxf=obj.schedule_forms)
        return EMSerializer(em).data

