from django.utils.timezone import now
from PIL import Image
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import forms

from onadata.apps.fieldsight.models import Organization


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_profile')
    address = models.CharField(max_length=140,blank=True, null=True)
    gender = models.CharField(max_length=140)
    phone = models.CharField(max_length=140, blank=True, null=True)
    skype = models.CharField(max_length=140, blank=True, null=True)
    primary_number = models.CharField(max_length=140, blank=True, null=True)
    secondary_number = models.CharField(max_length=140, blank=True, null=True)
    office_number = models.CharField(max_length=140, blank=True, null=True)
    viber = models.CharField(max_length=140, blank=True, null=True)
    whatsapp = models.CharField(max_length=140, blank=True, null=True)
    wechat = models.CharField(max_length=140, blank=True, null=True)
    line = models.CharField(max_length=140, blank=True, null=True)
    tango = models.CharField(max_length=140, blank=True, null=True)
    hike = models.CharField(max_length=140, blank=True, null=True)
    qq = models.CharField(max_length=140, blank=True, null=True)
    google_talk = models.CharField(max_length=140, blank=True, null=True)
    twitter = models.CharField(max_length=140, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=user_directory_path, default="logo/default_user.png")
    organization = models.ForeignKey(Organization, null=True, blank=True)
    notification_seen_date = models.DateTimeField(default=now, blank=True)
    logs = GenericRelation('eventlog.FieldSightLog')

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})

    def getname(self):
        return self.user.username

