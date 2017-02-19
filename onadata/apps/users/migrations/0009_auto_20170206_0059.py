# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20170206_0018'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name=b'cropping',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='image',
        ),
    ]
