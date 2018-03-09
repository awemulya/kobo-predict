# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0049_schedule_schedule_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='schedule_level',
        ),
        migrations.AddField(
            model_name='schedule',
            name='schedule_level_id',
            field=models.IntegerField(default=0, choices=[(0, 'Daily'), (1, 'Weekly'), (2, 'Monthly')]),
        ),
    ]
