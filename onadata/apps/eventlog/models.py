from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

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
        (7, 'XFORM'),
        (8, 'SUBMISSION_STATUS'),
    )
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    source = models.ForeignKey(User, related_name='log', null=True)
    organization = models.ForeignKey(Organization, related_name="logs", null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        get_latest_by = "-date"
        ordering = ["-date"]

    def get_absolute_url(self):
        return reverse('eventlog:notification-detail', kwargs={'pk': self.pk})

    def get_event_url(self):
        return self.content_object.get_absolute_url()




class FieldSightMessage(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver")
    msg_content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    @classmethod
    def inbox(cls, user):
        return FieldSightMessage.objects.filter(receiver=user, is_seen=False)

    @classmethod
    def outbox(cls, user):
        return FieldSightMessage.objects.filter(sender=user)

    @classmethod
    def user_messages(cls, user):
        return FieldSightMessage.objects.filter(Q(sender=user) | Q(receiver=user))

