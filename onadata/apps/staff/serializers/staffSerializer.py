from __future__ import unicode_literals
from rest_framework import serializers
from onadata.apps.staff.models import Staff, Attendance
from onadata.apps.users.serializers import UserSerializer


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        exclude = ()


class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        exclude = ()


