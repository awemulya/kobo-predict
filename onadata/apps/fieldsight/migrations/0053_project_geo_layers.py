# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_geolayer_tolerance'),
        ('fieldsight', '0052_auto_20180109_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='geo_layers',
            field=models.ManyToManyField(to='geo.GeoLayer', blank=True),
        ),
    ]
