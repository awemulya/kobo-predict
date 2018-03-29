# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0051_deletedxform'),
    ]

    operations = [
        migrations.AddField(
            model_name='deletedxform',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2018, 3, 22, 10, 3, 30, 483206, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
