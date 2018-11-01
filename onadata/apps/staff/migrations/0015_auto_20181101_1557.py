# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0014_auto_20181101_1154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='location',
        ),
        migrations.AddField(
            model_name='attendance',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True),
        ),
    ]
