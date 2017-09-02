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
        (1, 'User was added as the Project Manager of Project Name by Invitor Full Name.'),
        (2, 'User was added as Reviewer of Site Name by Invitor Full Name.'),
        (3, 'User was added as Site Supervisor of Site Name by Invitor Full Name.'),
        (4, 'User was assigned as an Organization Admin in Organization Name.'),
        (5, 'User was assigned as a Project Manager in Project Name.'),
        (6, 'User was assigned as a Reviewer in Site Name.'),
        (7, 'User was assigned as a Site Supervisor in Site Name.'),
        (8, 'User created a new organization named Organization Name'),
        (9, 'User created a new project named Project Name.'),
        (10, 'User created a new site named Site Name in Project Name.'),
        (11, 'User created number + sites in Project Name.'),
        (12, 'User changed the details of Organization Name.'),
        (13, 'User changed the details of Project Name.'),
        (14, 'User changed the details of Site Name.'),
        (15, 'User submitted a response for Form Type Form Name in Site Name.'),
        (16, 'User reviewed a response for Form Type Form Name in Site Name.'),
        (17, 'User assigned a new Form Type Form Name in Project Name.'),
        (18, 'User assigned a new Form Type Form Name to Site Name.'),
        (19, 'User edited Form Name form.'),
    )

   
    
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    seen_by = models.ManyToManyField(User, null=True)
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

