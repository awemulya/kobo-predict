from rest_framework import serializers

from onadata.apps.fsforms.models import Schedule, Days


class DaysSerializer(serializers.ModelSerializer):

    class Meta:
        model = Days
        exclude = ()


class ScheduleSerializer(serializers.ModelSerializer):

    # selected_days = DaysSerializer(many=True)
    days = serializers.SerializerMethodField('get_all_days', read_only=True)

    class Meta:
        model = Schedule
        exclude = ('group', 'date_created', 'shared_level', 'selected_days')

    def get_all_days(self, obj):
        return u"%s" % (", ".join(day.day for day in obj.selected_days.all()))

