# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_remove_userprofile_multiple_org'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='notification_seen_date',
            field=models.DateTimeField(default=django.utils.timezone.now, blank=True),
        ),
    ]
