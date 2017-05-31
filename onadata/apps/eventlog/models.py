from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from onadata.apps.fieldsight.models import Organization

user_type = ContentType.objects.get(app_label="users", model="userprofile")


class FieldSightLog(models.Model):
    ACTION_TYPES = (
        (0, 'USER'),
        (1, 'FORM'),
        (2, 'SUBMISSION'),
        (3, 'Site'),
        (4, 'Project'),
        (5, 'Organization'),
        (6, 'Role'),
    )
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    source = models.ForeignKey(User, related_name='log', null=True)
    organization = models.ForeignKey(Organization, related_name="logs")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        get_latest_by = "-date"
        ordering = ["-date"]

    def get_absolute_url(self):
        if self.content_type == user_type :
            return reverse('users:profile', kwargs={'pk': self.content_object.user.pk})
        return "#"

