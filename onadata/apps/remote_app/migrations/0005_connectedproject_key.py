# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('remote_app', '0004_remoteapp_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='connectedproject',
            name='key',
            field=models.CharField(default='test', max_length=255),
            preserve_default=False,
        ),
    ]
