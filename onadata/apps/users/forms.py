from __future__ import unicode_literals
from django import forms
from PIL import Image
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from onadata.apps.fieldsight.models import Organization
from .models import UserProfile
from django.contrib.auth.models import User


import StringIO
import re
import mimetypes
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class LoginForm(forms.Form):
    username = forms.CharField(label='Your Email/Username', max_length=100)
    password = forms.CharField(label='Your Password', max_length=100)


class SignUpForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
    email = forms.EmailField(label='Email address', required=True)
    password = forms.CharField(widget=forms.PasswordInput,label='Your Password', max_length=100)
    password1 = forms.CharField(widget=forms.PasswordInput,label='One more time?', max_length=100)

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()
        password = self.cleaned_data.get('password')
        password1 = self.cleaned_data.get('password1')
        if password != password1:
            raise ValidationError({'password':['The passwords did not match']})
        
        else:
            if len(password) < 8:
                raise ValidationError({'password': ['Passwords must be of more than 8 characters']})
            
            pattern = re.compile(r"^[w\d_-]+$")
            if not bool(pattern.search(password)):
                raise ValidationError({'password': ['Password must contain alphabet characters, special characters and numbers']})

    def clean_email(self):
        email = self.cleaned_data['email']
        if validate_email(email)==False:
            raise ValidationError('Enter a valid Email address')
        
        if User.objects.filter(email=email):
            raise ValidationError('User with this email already exists')

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username):
            raise ValidationError('User with this username already exists')


class ProfileForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(label="First Name", required=True)
    last_name = forms.CharField(label="Last Name", required=True)
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
        fields = ['first_name','last_name','address','gender','phone','skype','primary_number','secondary_number'
            ,'office_number', 'viber', 'whatsapp', 'wechat', 'line', 'tango', 'hike', 'qq', 'google_talk', 'twitter',
                  'profile_picture', 'timezone',]

    def save(self):
        photo = super(ProfileForm, self).save()
        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')
        if x is not None and y is not None:
            image = Image.open(photo.profile_picture)
            cropped_image = image.crop((x, y, w+x, h+y))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            # resized_image.save(photo.profile_picture.path)
            resized_image_file = StringIO.StringIO()
            mime = mimetypes.guess_type(photo.profile_picture.name)[0]
            plain_ext = mime.split('/')[1]
            resized_image.save(resized_image_file, plain_ext)
            default_storage.delete(photo.profile_picture.name)
            default_storage.save(photo.profile_picture.name, ContentFile(resized_image_file.getvalue()))
            resized_image_file.close()
        return photo

    # def clean_profile_picture(self):
    #     image = self.cleaned_data.get('profile_picture')
    #     if image:
    #         from django.core.files.images import get_image_dimensions
    #         w, h = get_image_dimensions(image)
    #         if (235 <= h <= 245) and  (235 <= w <= 245):
    #             return image
    #         raise forms.ValidationError(_(u'The image Size needs to be 250 * 250 PX '))
    #


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

