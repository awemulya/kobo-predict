from __future__ import unicode_literals
from rest_framework import serializers
from onadata.apps.staff.models import Staff, Attendance, Team
from onadata.apps.users.serializers import UserSerializer
from rest_framework.exceptions import ValidationError


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
        exclude = ('created_date', 'updated_date', 'submitted_by', 'team')

    def create(self, validated_data):
        # Remove nested and M2m relationships from validated_data
        staffs = validated_data.pop('staffs') if 'staffs' in validated_data else []

        # Create project model
        instance = Attendance.objects.create(**validated_data)
        instance.save()
        instance.staffs = staffs
        instance.save()
        return instance




