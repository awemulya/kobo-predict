from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from registration import forms as registration_forms

from onadata.apps.fieldsight.helpers import AdminImageWidget
from .utils.forms import HTML5BootstrapModelForm, KOModelForm
from .models import Organization, Project, Site, BluePrints
from onadata.apps.userrole.models import UserRole

USERNAME_REGEX = r'^[a-z][a-z0-9_]+$'
USERNAME_MAX_LENGTH = 30
USERNAME_INVALID_MESSAGE = _(
    'A username may only contain lowercase letters, numbers, and '
    'underscores (_).'
)


class RegistrationForm(registration_forms.RegistrationFormUniqueEmail):

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['organization'].choices = [(org.id, org.name) for org in Organization.objects.all()]
        self.fields['organization'].empty_label = None

    organization = forms.ChoiceField(widget = forms.Select(), required=False)
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
        widgets = {
        'location': forms.HiddenInput(),
        'address': forms.TextInput(),
        'logo': AdminImageWidget()
        }


    def clean(self):
        lat = self.data.get("Longitude","85.3240")
        long = self.data.get("Latitude","27.7172")
        p = Point(float(lat), float(long),srid=4326)
        self.cleaned_data["location"] = p
        super(OrganizationForm, self).clean()


class AssignOrgAdmin(HTML5BootstrapModelForm, KOModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(AssignOrgAdmin, self).__init__(*args, **kwargs)
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.organization.get_staffs
            old_admins_id = [admin[0] for admin in old_admins]
            old_admins_id.append(settings.ANONYMOUS_USER_ID)
            if hasattr(self.request, "organization"):
                if self.request.organization:
                    users = User.objects.filter(user_profile__organization=self.request.organization, is_active=True).\
                        filter(id__in=old_admins_id)
                else:
                    users = User.objects.filter(is_active=True).exclude(id__in=old_admins_id)
            else:
                users = User.objects.filter(is_active=True).exclude(id__in=old_admins_id)
            self.fields['user'].queryset = users
            self.fields['organization'].choices = old_admins

    class Meta:
        fields = ['user', 'group', 'organization']
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


class SetProjectRoleForm(HTML5BootstrapModelForm, KOModelForm):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(SetProjectRoleForm, self).__init__(*args, **kwargs)
        self.fields['group'].empty_label = None
        role = kwargs.get('instance')
        if role is not None:
            old_admins = role.project.get_staffs_both_role
            old_admins.append(settings.ANONYMOUS_USER_ID)
            if hasattr(self.request, "organization"):
                if self.request.organization:
                    users = User.objects.filter(is_active=True, user_profile__organization=self.request.organization)\
                        .exclude(id__in=old_admins)
                else:
                    users = User.objects.filter(is_active=True).exclude(id__in=old_admins)
            else:
                users = User.objects.filter(is_active=True).exclude(id__in=old_admins)
            self.fields['user'].queryset = users
        self.fields['group'].queryset = Group.objects.filter(
            name__in=['Project Manager', 'Reviewer', 'Central Engineer'])

    class Meta:
        fields = ['user', 'group','project']
        model = UserRole
        widgets = {
            'user': forms.Select(attrs={'class': 'selectize', 'data-url': reverse_lazy('role:user_add')}),
            'group': forms.Select(attrs={'class':'select', 'name': 'group', 'id':'value', 'onchange':'Hide()'}),
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
        widgets = {
        'address': forms.TextInput(),
        'location': forms.HiddenInput(),
        'logo': AdminImageWidget()
        }

    def clean(self):
        lat = self.data.get("Longitude", "85.3240")
        long = self.data.get("Latitude", "27.7172")
        p = Point(float(lat), float(long), srid=4326)
        self.cleaned_data["location"] = p
        super(ProjectForm, self).clean()


class SiteForm(HTML5BootstrapModelForm, KOModelForm):
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
        widgets = {
        'address': forms.TextInput(),
        # 'location': gform.OSMWidget(attrs={'map_width': 400, 'map_height': 400}),
        'location': forms.HiddenInput(),
        'logo': AdminImageWidget()
        }

    def clean(self):
        lat = self.data.get("Longitude","85.3240")
        long = self.data.get("Latitude","27.7172")
        p = Point(float(lat), float(long),srid=4326)
        self.cleaned_data["location"] = p
        super(SiteForm, self).clean()


class UploadFileForm(forms.Form):
    file = forms.FileField()


class BluePrintForm(forms.ModelForm):
    image = forms.ImageField(label='Image')

    class Meta:
        model = BluePrints
        fields = ('image', )