from rest_framework import serializers

from onadata.apps.fsforms.models import Schedule, Days


class DaysSerializer(serializers.ModelSerializer):
    selected = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Days
        exclude = ()

    def get_selected(self, obj):
        return False


class ScheduleSerializer(serializers.ModelSerializer):

    days = serializers.SerializerMethodField('get_all_days', read_only=True)

    class Meta:
        model = Schedule
        exclude = ('date_created', 'shared_level')

    def get_all_days(self, obj):
        return u"%s" % (", ".join(day.day for day in obj.selected_days.all()))

