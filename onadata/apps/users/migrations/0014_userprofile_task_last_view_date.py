# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_userprofile_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='task_last_view_date',
            field=models.DateTimeField(default=datetime.datetime(2018, 11, 12, 11, 17, 44, 268976, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
