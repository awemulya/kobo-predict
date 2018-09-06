# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0063_auto_20180620_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='current_progress',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
