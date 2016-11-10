from django.db import models

from onadata.apps.fieldsight.models import Site
from onadata.apps.logger.models import XForm


class Stages(models.Model):
    name = models.CharField(max_length=256)


class FieldSightXF(models.Model):
    xf = models.Foreignkey(XForm)
    site = models.ManyToManyField(Site, related_name="site_forms", blank=True)
    scheduled = models.BooleanField(default=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    stage = models.ForeignKey(Stages, blank=True, null=True)
