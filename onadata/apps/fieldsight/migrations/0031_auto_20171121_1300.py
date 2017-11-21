# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0030_auto_20171121_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timezone',
            name='offset_time',
            field=models.CharField(max_length=255, blank=True),
        ),
    ]
