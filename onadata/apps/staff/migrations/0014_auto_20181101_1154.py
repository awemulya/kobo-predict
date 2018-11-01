# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0013_auto_20180601_1433'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, geography=True, blank=True),
        ),
        migrations.AlterField(
            model_name='staff',
            name='designation',
            field=models.IntegerField(default=1, choices=[(1, b'TSC Agent'), (2, b'Social Mobilizer'), (3, b'Senior Builder-Trainer'), (4, b'Junior Builder-Trainer'), (5, b'Team Leader'), (6, b'Support Staff'), (7, b'Field Supervisor'), (8, b'Community Messenger')]),
        ),
    ]
