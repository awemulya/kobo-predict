from __future__ import unicode_literals
import json
from rest_framework import serializers
from onadata.apps.staff.models import Staff, Attendance, Team, Bank
from onadata.apps.users.serializers import UserSerializer
from rest_framework.exceptions import ValidationError


class BankSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bank
        fields = ('id', 'name', )

class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ('id', 'name', )


class StaffSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Staff
        exclude = ('created_by', 'team', 'created_date', 'updated_date', 'is_deleted',)

    def create(self, validated_data):
        bank_id = validated_data.pop('bank') if 'bank' in validated_data else None
        instance = Staff.objects.create(**validated_data)
        try:
            if bank_id:
                instance.bank = bank_id
                instance.bank_name = ''

            else:
                if instance.bank_name == "":
                    raise ValidationError("Got empty bank name. Provide either bank id or bank name.")     
            instance.save()
        
        except Exception as e:
            raise ValidationError("Got error on: {}".format(e))

        return instance

class AttendanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        exclude = ('created_date', 'updated_date', 'submitted_by', 'team')

    def create(self, validated_data):
        try:
            staffs = validated_data.pop('staffs') if 'staffs' in validated_data else []
            instance = Attendance.objects.create(**validated_data)
            instance.save()
        
            
            if not staffs:
                instance.delete()
                raise ValidationError("Got Empty staffs list.")

            else:
                for staff in staffs:
                    if int(staff.team_id) != int(instance.team_id):
                        instance.delete()
                        raise ValidationError("Got error on: Staffs entered has different team.")
                
            instance.staffs = staffs
            instance.save()
        
        except Exception as e:
            raise ValidationError("Got error on: {}".format(e))
        return instance




