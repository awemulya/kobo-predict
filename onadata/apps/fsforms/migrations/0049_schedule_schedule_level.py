# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0048_auto_20180109_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='schedule_level',
            field=models.IntegerField(default=0, choices=[(0, 'Daily'), (1, 'Monthly'), (2, 'Weekly')]),
        ),
    ]
