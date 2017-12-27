from __future__ import unicode_literals
import json
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from onadata.apps.fieldsight.models import Organization, Project, Site
from onadata.apps.users.models import UserProfile
from django.http import JsonResponse
from celery.result import AsyncResult

user_type = ContentType.objects.get(app_label="users", model="userprofile")


class FieldSightLog(models.Model):
    ACTION_TYPES = (
        (1, 'User was added as the Organization Admin of Organization Name by Invitor Full Name.'),
        (2, 'User was added as the Project Manager of Project Name by Invitor Full Name.'),
        (3, 'User was added as Reviewer of Site Name by Invitor Full Name.'),
        (4, 'User was added as Site Supervisor of Site Name by Invitor Full Name.'),
        (5, 'User was assigned as an Organization Admin in Organization Name.'),
        (6, 'User was assigned as a Project Manager in Project Name.'),
        (7, 'User was assigned as a Reviewer in Site Name.'),
        (8, 'User was assigned as a Site Supervisor in Site Name.'),
        (9, 'User created a new organization named Organization Name'),
        (10, 'User created a new project named Project Name.'),
        (11, 'User created a new site named Site Name in Project Name.'),
        (12, 'User created number + sites in Project Name.'),
        (13, 'User changed the details of Organization Name.'),
        (14, 'User changed the details of Project Name.'),
        (15, 'User changed the details of Site Name.'),
        (16, 'User submitted a response for Form Type Form Name in Site Name.'),
        (17, 'User reviewed a response for Form Type Form Name in Site Name.'),
        (18, 'User assigned a new Form Type Form Name in Project Name.'),
        (19, 'User assigned a new Form Type Form Name to Site Name.'),
        (20, 'User edited Form Name form.'),
    )
    
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    seen_by = models.ManyToManyField(User)
    source = models.ForeignKey(User, related_name='log', null=True)
    organization = models.ForeignKey(Organization, related_name="logs", null=True)
    project = models.ForeignKey(Project, related_name="logs", null=True)
    site = models.ForeignKey(Site, related_name="logs", null=True)
    extra_message = models.CharField(max_length=255, blank=True, null=True)
    
    recipient = models.ForeignKey(User, related_name='recipent_log', null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    extra_content_type = models.ForeignKey(ContentType, related_name='notify_object', blank=True, null=True)
    extra_object_id = models.CharField(max_length=255, blank=True, null=True)
    extra_object = GenericForeignKey('extra_content_type', 'extra_object_id')
    

    class Meta:
        get_latest_by = "-date"
        ordering = ["-date"]

    def get_absolute_url(self):
        return reverse('eventlog:notification-detail', kwargs={'pk': self.pk})

    def get_event_url(self):
        return self.content_object.get_absolute_url()

    def get_event_name(self):
        return self.content_object.getname()

    def get_extraobj_url(self):
        if self.extra_object is None:
            return None
        if self.extra_content_type.name == 'user':
            if self.extra_object.user_profile:
                return self.extra_object.user_profile.get_absolute_url()
            return "#";
        return self.extra_object.get_absolute_url()

    def get_extraobj_name(self):
        if self.extra_object is None:
            return None
        if self.extra_content_type.name == 'user':
            if self.extra_object.user_profile:
                return self.extra_object.user_profile.getname()
            return self.extra_object.email
        return self.extra_object.getname()

    def get_source_url(self):
        try:
            profile = self.source.user_profile
        except UserProfile.DoesNotExist:
            return None
        else:
            return profile.get_absolute_url()

    def get_org_url(self):
        if self.organization is None:
            return None
        return self.organization.get_absolute_url()

    def get_project_url(self):
        if self.project is None:
            return None
        return self.project.get_absolute_url()

    def get_site_url(self):
        if self.site is None:
            return None
        return self.site.get_absolute_url()

    def __str__(self):
        return str(self.get_type_display())


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


class CeleryTaskProgress(models.Model):
    Task_Status =(
        (0, 'Pending'),
        (1, 'In Progress'),
        (2, 'Completed'),
        (3, 'Failed'),
        )
    Task_Type =(
        (0, 'Bulk Site Upload'),
        (1, 'Multi User Assign Project'),
        (2, 'Multi User Assign Site')
        )
    task_id = models.CharField(max_length=255, unique=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(User, related_name="task_owner")
    status = models.IntegerField(default=0, choices=Task_Status)
    description = models.CharField(max_length=755, blank=True)
    task_type = models.IntegerField(default=0, choices=Task_Type)
    content_type = models.ForeignKey(ContentType, related_name='task_object', blank=True, null=True)
    object_id = models.CharField(max_length=255, blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def get_progress(self):
        if self.status == 1:
            task = AsyncResult(self.task_id)
            data = task.result or task.state
            return json.dumps(data)
        return None




