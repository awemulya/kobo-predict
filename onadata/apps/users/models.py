from django.db import models
from django.conf import settings


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<username>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile')
    address = models.CharField(max_length=140)
    gender = models.CharField(max_length=140)
    phone = models.CharField(max_length=140)
    skype = models.CharField(max_length=140)
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True)

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username
