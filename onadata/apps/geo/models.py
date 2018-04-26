from __future__ import unicode_literals

from onadata.apps.fieldsight.models import Organization
from django.contrib.gis.db import models


class GeoLayer(models.Model):
    organization = models.ForeignKey(Organization,
                                     related_name='geo_layers',
                                     on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    title = models.CharField(max_length=255)
    title_prop = models.CharField(max_length=255, blank=True)
    code_prop = models.CharField(max_length=255, blank=True)
    geo_shape_file = models.FileField(upload_to='geo_layers/')
    stale_areas = models.BooleanField(default=True)
    tolerance = models.FloatField(default=0.0001)

    class Meta:
        ordering = ['title', 'level']

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        from .loader import load_areas
        super(GeoLayer, self).save(*args, **kwargs)

        if self.stale_areas:
            load_areas(self)


class GeoArea(models.Model):
    geo_layer = models.ForeignKey(GeoLayer,
                                  related_name='geo_areas',
                                  on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, blank=True)
    geometry = models.GeometryField(null=True, blank=True, default=None)

    def __unicode__(self):
        return self.title
