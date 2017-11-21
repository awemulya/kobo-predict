# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0028_auto_20171120_1657'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timezone',
            old_name='country',
            new_name='country_name',
        ),
        migrations.RenameField(
            model_name='timezone',
            old_name='offset_time',
            new_name='gmt_offset',
        ),
        migrations.AddField(
            model_name='timezone',
            name='time_zone',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
