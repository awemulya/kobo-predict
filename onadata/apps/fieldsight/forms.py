from django import forms
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from registration import forms as registration_forms

from onadata.utils.forms import HTML5BootstrapModelForm, KOModelForm
from .models import Organization, Project, Site
from onadata.apps.userrole.models import UserRole

USERNAME_REGEX = r'^[a-z][a-z0-9_]+$'
USERNAME_MAX_LENGTH = 30
USERNAME_INVALID_MESSAGE = _(
    'A username may only contain lowercase letters, numbers, and '
    'underscores (_).'
)

organization_list = [(org.id, org.name) for org in Organization.objects.filter(is_active=True)]


class RegistrationForm(registration_forms.RegistrationFormUniqueEmail):
    organization = forms.ChoiceField(widget = forms.Select(),
                     choices = organization_list, required=False,)
    username = forms.RegexField(
        regex=USERNAME_REGEX,
        max_length=USERNAME_MAX_LENGTH,
        label=_("Username"),
        error_messages={'invalid': USERNAME_INVALID_MESSAGE}
    )
    name = forms.CharField(
        label=_('Full Name'),
        required=True,
    )

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
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.get_staffs_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_admins)
            self.fields['user'].choices = [(user.pk, user.username) for user in users]

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
        'user': forms.CheckboxSelectMultiple()
        }


class AssignOrgAdmin(HTML5BootstrapModelForm, KOModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(AssignOrgAdmin, self).__init__(*args, **kwargs)
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.organization.get_staffs_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_admins)
            if hasattr(self.request,"organization"):
                if self.request.organization:
                    users = users.filter(user_profile__organization=self.request.organization)
            self.fields['user'].queryset = users

    class Meta:
        fields = ['user','group','organization']
        model = UserRole
        widgets = {
            'user': forms.Select(attrs={'class': 'selectize', 'data-url': reverse_lazy('role:user_add')}),
            'group': forms.HiddenInput(),
            'organization': forms.HiddenInput()
        }


class SetProjectManagerForm(HTML5BootstrapModelForm, KOModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SetProjectManagerForm, self).__init__(*args, **kwargs)
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.project.get_staffs_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_admins)
            if hasattr(self.request, "organization"):
                if self.request.organization:
                    users = users.filter(user_profile__organization=self.request.organization)
            self.fields['user'].queryset = users

    class Meta:
        fields = ['user','group','project']
        model = UserRole
        widgets = {
            'user': forms.Select(attrs={'class': 'selectize', 'data-url': reverse_lazy('role:user_add')}),
            'group': forms.HiddenInput(),
            'project': forms.HiddenInput()
        }


class SetSupervisorForm(HTML5BootstrapModelForm, KOModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SetSupervisorForm, self).__init__(*args, **kwargs)
        role = kwargs.get('instance')
        if role is not None:
            old_pm = role.site.get_supervisor_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_pm)
            if hasattr(self.request, "organization"):
                if self.request.organization:
                    users = users.filter(user_profile__organization=self.request.organization)
            self.fields['user'].queryset = users

    class Meta:
        fields = ['user']
        model = UserRole
        widgets = {
            'user': forms.Select(attrs={'class': 'selectize', 'data-url': reverse_lazy('role:user_add')}),
            'group': forms.HiddenInput(),
            'project': forms.HiddenInput()
        }


class SetCentralEngForm(HTML5BootstrapModelForm, KOModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SetCentralEngForm, self).__init__(*args, **kwargs)
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.project.get_central_eng_id
            users = User.objects.filter().exclude(id=settings.ANONYMOUS_USER_ID).exclude(id__in=old_admins)
            if hasattr(self.request, "organization"):
                if self.request.organization:
                    users = users.filter(user_profile__organization=self.request.organization)
            self.fields['user'].queryset = users

    class Meta:
        fields = ['user','group','project']
        model = UserRole
        widgets = {
            'user': forms.Select(attrs={'class': 'selectize', 'data-url': reverse_lazy('role:user_add')}),
            'group': forms.HiddenInput(),
            'project': forms.HiddenInput()
        }



class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)
        self.fields['type'].empty_label = None
        self.fields['organization'].empty_label = None

    class Meta:
        model = Project
        exclude = []
        organization_filters = ['organization']


class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        if not self.fields['location'].initial:
            self.fields['location'].initial = Point(85.3240, 27.7172,srid=4326)
        self.fields['type'].empty_label = None
        self.fields['project'].empty_label = None

    class Meta:
        model = Site
        exclude = []
        project_filters = ['project']


