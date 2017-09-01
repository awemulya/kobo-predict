from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from onadata.apps.fieldsight.models import Organization, Project, Site

user_type = ContentType.objects.get(app_label="users", model="userprofile")


class FieldSightLog(models.Model):
    ACTION_TYPES = (
        (0, 'User joined Organization Name as an Organization Admin.'),
        (1, 'User was added as the Project Manager of Project Name by Invitor Full Name '),
        (2, 'User was added as Reviewer of Site Name by Invitor Full Name '),
        (3, 'User was added as Site Supervisor of Site Name by Invitor Full Name '),
        (2, 'User was assigned as an Organization Admin in Organization Name'),
        (3, 'Site'),
        (4, 'Project'),
        (5, 'Organization'),
        (6, 'Role'),
        (7, 'XFORM'),
        (8, 'SUBMISSION_STATUS'),
        (9, 'UserInvite'),
    )

    NOTIFICATION_TYPES=(
        (0, ''),
        (1, ''),
        (2, ''),
        (3, ''),
        (4, ''),
        (5, ''),
        (6, ''),
        (7, ''),
        (8, ''),
        (9, ''),
        (10, ''),
        (11, ''),
        (12, ''),
        (13, ''),
        (14, ''),
        (15, ''),
        (16, ''),
        (17, ''),
        (18, ''),
        (19, ''),
        )
    
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    seen_by = models.ManyToManyField(null=True)
    source = models.ForeignKey(User, related_name='log', null=True)
    organization = models.ForeignKey(Organization, related_name="logs", null=True)
    project = models.ForeignKey(Project, related_name="logs", null=True)
    site = models.ForeignKey(Site, related_name="logs", null=True)
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

