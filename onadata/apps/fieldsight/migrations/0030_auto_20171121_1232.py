# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0029_auto_20171121_1111'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timezone',
            old_name='country_name',
            new_name='country',
        ),
        migrations.RenameField(
            model_name='timezone',
            old_name='gmt_offset',
            new_name='offset_time',
        ),
        migrations.RemoveField(
            model_name='timezone',
            name='time_zone',
        ),
    ]
