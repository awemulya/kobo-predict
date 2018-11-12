# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_userprofile_task_last_view_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='task_last_view_date',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
    ]
