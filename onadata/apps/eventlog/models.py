from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        get_latest_by = "date"
        ordering = ["-date", "type"]
