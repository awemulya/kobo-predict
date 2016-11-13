from django.db import models

from onadata.apps.fieldsight.models import Site
from onadata.apps.logger.models import XForm


class Stages(models.Model):
    name = models.CharField(max_length=256)
    order = models.IntegerField()

class SubStage(models.Model):
    name = models.CharField(max_length=256)
    order_no = models.IntegerField
    stage = models.ForeignKey(Stages, related_name="sub_stage")


class FieldSightXF(models.Model):
    xf = models.Foreignkey(XForm)
    site = models.ManyToManyField(Site, related_name="site_forms", blank=True)
    scheduled = models.BooleanField(default=True)
    start = models.DateField(blank=True, null=True)
    end = models.DateField(blank=True, null=True)
    sub_stage = models.ForeignKey(SubStage, blank=True, null=True)
