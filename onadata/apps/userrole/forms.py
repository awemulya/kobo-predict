from django import forms
from django.contrib.auth.models import User
from django.conf import settings

from .models import UserRole


class UserRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = None
        self.fields['user'].empty_label = None
        users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID)
        self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        model = UserRole
        exclude = []