# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20170206_0059'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='multiple_org',
            field=models.BooleanField(default=False),
        ),
    ]
