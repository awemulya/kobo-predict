from django import forms
from django.utils.translation import ugettext_lazy as _
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
        fields = ['address','gender','phone', 'skype', 'profile_picture', 'user']
        widgets = {'user': forms.HiddenInput()}


