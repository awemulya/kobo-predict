# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0041_auto_20190114_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='event_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='event_url',
            field=models.CharField(max_length=500, blank=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_obj_name',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_obj_url',
            field=models.CharField(max_length=500, blank=True),
        ),
    ]
