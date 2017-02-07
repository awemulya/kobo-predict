from django import forms
from django.contrib.auth.models import User
from django.conf import settings

from onadata.apps.fieldsight.models import Organization
from onadata.utils.forms import HTML5BootstrapModelForm
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


class UserForm(HTML5BootstrapModelForm):
    organization = forms.ChoiceField(widget = forms.Select(), required=False,)

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['organization'].choices = [(org.id, org.name) for org in Organization.objects.all()]
        self.fields['organization'].empty_label = None

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "is_active", "email", "organization",)
