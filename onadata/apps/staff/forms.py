from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from onadata.apps.staff.models import Team, StaffProject, Bank, Staff
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
        self.fields['bank'].choices = [(bank.id, role.name) for bank in Bank.objects.all()]
    
    class Meta:
        model = Staff
        fields = ('first_name','last_name', 'gender', 'ethnicity','address','phone_number','bank_name', 'bank', 'account_number', 'photo', 'designation',)

