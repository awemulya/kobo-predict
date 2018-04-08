from __future__ import unicode_literals
from rest_framework import serializers
from onadata.apps.staff.models import Staff, Attendance, Team
from onadata.apps.users.serializers import UserSerializer


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('id', 'name',)


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        exclude = ('created_by', 'team', 'created_date', 'updated_date',)


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        exclude = ('created_date', 'updated_date', 'submitted_by')


