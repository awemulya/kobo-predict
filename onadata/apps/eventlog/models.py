from django.contrib.auth.models import User
from django.db import models

# Create your models here.
<<<<<<< HEAD
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
=======
from onadata.apps.fsforms.models import FieldSightXF, FInstance
from onadata.apps.users.models import UserProfile
from onadata.apps.fieldsight.models import Site
>>>>>>> restful-projects-api


class FieldSightLog(models.Model):
    ACTION_TYPES = (
        (0, 'USER'),
        (1, 'FORM'),
        (2, 'SUBMISSION'),
        (3, 'Site'),
<<<<<<< HEAD
        (4, 'Project'),
        (5, 'Organization'),
        (6, 'Role'),
=======
>>>>>>> restful-projects-api
    )
    type = models.IntegerField(default=0, choices=ACTION_TYPES)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
<<<<<<< HEAD
    is_seen = models.BooleanField(default=False)
    source = models.ForeignKey(User, related_name='log', null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
=======
    profile = models.ForeignKey(UserProfile, related_name="log", null=True)
    form = models.ForeignKey(FieldSightXF, related_name="log", null=True)
    instance = models.ForeignKey(FInstance, related_name="log", null=True)
    site = models.ForeignKey(Site, related_name="log", null=True)
    is_seen = models.BooleanField(default=False)
    source = models.ForeignKey(User, related_name='log', null=True)
>>>>>>> restful-projects-api

    class Meta:
        get_latest_by = "date"
        ordering = ["-date", "type"]
