from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from onadata.apps.fieldsight.models import Organization
from .models import UserProfile


class LoginForm(forms.Form):
    email = forms.EmailField(label='Your Email', max_length=100)
    password = forms.CharField(label='Your Email', max_length=100)


class ProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(
        label=_('Gender'),
        required=False,
        choices=(
                 ('male', _('Male')),
                 ('female', _('Female')),
                 ('other', _('Other')),
                 )
    )

    class Meta:
        model = UserProfile
        exclude = ['user']

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            from django.core.files.images import get_image_dimensions
            w, h = get_image_dimensions(image)
            if (235 <= h <= 245) and  (235 <= w <= 245):
                return image
            raise forms.ValidationError(_(u'The image Size needs to be 250 * 250 PX '))



class UserEditForm(forms.Form):
    name = forms.CharField(label=_("Full Name"), required=True)
    gender = forms.ChoiceField(
        label=_('Gender'),
        required=False,
        choices=(
                 ('male', _('Male')),
                 ('female', _('Female')),
                 ('other', _('Other')),
                 )
    )
    address = forms.CharField(label=_("Address"), required=False)
    phone = forms.CharField(label=_("Phone"), required=False)
    skype = forms.CharField(label=_("Skype"), required=False)
    primary_number = forms.CharField(required=False)
    secondary_number = forms.CharField(required=False)
    office_number = forms.CharField(required=False)
    viber = forms.CharField(required=False)
    whatsapp = forms.CharField(required=False)
    wechat = forms.CharField(required=False)
    line = forms.CharField(required=False)
    tango = forms.CharField(required=False)
    hike = forms.CharField(required=False)
    qq = forms.CharField(required=False)
    google_talk = forms.CharField(required=False)
    twitter = forms.CharField(required=False)

