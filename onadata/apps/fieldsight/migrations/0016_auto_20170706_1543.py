# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0015_chatmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 6, 9, 58, 30, 682140, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 6, 9, 58, 38, 322473, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2017, 7, 6, 9, 58, 57, 81816, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
