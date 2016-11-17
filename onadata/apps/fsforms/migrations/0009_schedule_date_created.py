# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0008_auto_20161117_0335'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 17, 3, 43, 40, 404634), auto_now_add=True),
            preserve_default=False,
        ),
    ]
