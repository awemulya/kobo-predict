from django import forms
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext_lazy as _
from registration import forms as registration_forms

from django.conf import settings

from onadata.apps.logger.models import XForm
from .models import Organization, Project, Site, UserRole

USERNAME_REGEX = r'^[a-z][a-z0-9_]+$'
USERNAME_MAX_LENGTH = 30
USERNAME_INVALID_MESSAGE = _(
    'A username may only contain lowercase letters, numbers, and '
    'underscores (_).'
)


class RegistrationForm(registration_forms.RegistrationFormUniqueEmail):
    username = forms.RegexField(
        regex=USERNAME_REGEX,
        max_length=USERNAME_MAX_LENGTH,
        label=_("Username"),
        error_messages={'invalid': USERNAME_INVALID_MESSAGE}
    )
    name = forms.CharField(
        label=_('Full Name'),
        required=False,
    )
    # organization = forms.CharField(
    #     label=_('Organization name'),
    #     required=False,
    # )

    is_active = forms.BooleanField(
        label=_('Active'),
        required=False,
        initial=True
    )


    class Meta:
        model = User
        fields = [
            'name',
            'username',
            'email',
             # The 'password' field appears without adding it here; adding it
            # anyway results in a duplicate
        ]


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)
        self.fields['type'].empty_label = None

    class Meta:
        model = Organization
        exclude = []
        # exclude = ['organizaton']


class SetOrgAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetOrgAdminForm, self).__init__(*args, **kwargs)
        org = kwargs.get('instance')
        if org is not None:
            old_admins = org.get_staffs_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_admins)
            self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
        'users': forms.CheckboxSelectMultiple()
        }


class SetProjectManagerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetProjectManagerForm, self).__init__(*args, **kwargs)
        org = kwargs.get('instance')
        if org is not None:
            old_pm = org.get_staffs_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_pm)
            self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
        'users': forms.CheckboxSelectMultiple()
        }


class SetSupervisorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetSupervisorForm, self).__init__(*args, **kwargs)
        org = kwargs.get('instance')
        if org is not None:
            old_pm = org.get_supervisor_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_pm)
            self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
        'users': forms.CheckboxSelectMultiple()
        }


class SetCentralEngForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SetCentralEngForm, self).__init__(*args, **kwargs)
        org = kwargs.get('instance')
        if org is not None:
            old_pm = org.get_central_eng_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_pm)
            self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
        'users': forms.CheckboxSelectMultiple()
        }


class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)
        self.fields['type'].empty_label = None

    class Meta:
        model = Project
        exclude = ['organization']


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)
        self.fields['type'].empty_label = None

    class Meta:
        model = Site
        exclude = ['project']


class UserRoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = None
        self.fields['user'].empty_label = None

    class Meta:
        model = UserRole
        exclude = []


class AssignSettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AssignSettingsForm, self).__init__(*args, **kwargs)
        # sites = Site.objects.all()

    class Meta:
        fields = ['site']
        model = XForm
        widgets = {
        'site': forms.CheckboxSelectMultiple()
        }

