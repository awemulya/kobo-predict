from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from onadata.apps.fieldsight.models import Organization


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_profile')
    address = models.CharField(max_length=140)
    gender = models.CharField(max_length=140)
    phone = models.CharField(max_length=140)
    skype = models.CharField(max_length=140)
    profile_picture = models.ImageField(upload_to=user_directory_path, default="logo/default_image.png")
    organization = models.ForeignKey(Organization, null=True, blank=True)

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username
