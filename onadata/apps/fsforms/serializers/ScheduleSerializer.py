from rest_framework import serializers

from onadata.apps.fsforms.models import Schedule, Days, FieldSightXF


class DaysSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Days
        exclude = ()

    def get_selected(self, obj):
        return False


class ScheduleSerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField('get_all_days', read_only=True)
    form = serializers.SerializerMethodField('get_assigned_form', read_only=True)

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
                return fsxf.xf.id
        return None

