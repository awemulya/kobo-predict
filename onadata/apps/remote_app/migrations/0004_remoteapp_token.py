# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_app', '0003_auto_20180628_0647'),
    ]

    operations = [
        migrations.AddField(
            model_name='remoteapp',
            name='token',
            field=models.TextField(blank=True),
        ),
    ]
