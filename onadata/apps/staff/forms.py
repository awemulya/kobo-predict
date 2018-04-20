from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from onadata.apps.staff.models import Team, StaffProject, Bank, Staff, Attendance
from onadata.apps.userrole.models import UserRole

class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['leader'].choices = [(role.user.id, role.user.username) for role in UserRole.objects.filter(project_id__in=[137,105,129], ended_at=None).distinct('user_id')]
    
    class Meta:
        model = Team
        fields = ('leader','name')


class StaffForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StaffForm, self).__init__(*args, **kwargs)
        self.fields['bank'].empty_label = "Other"
       
    
    class Meta:
        model = Staff
        fields = ('first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank','bank_name', 'account_number', 'photo', 'designation',)

class AttendanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.fields['staffs'].choices = [(staff.id, staff) for staff in Staff.objects.filter(team_id=kwargs.get('instance').team_id)]
    
    class Meta:
        model = Attendance
        fields = ('staffs',)
