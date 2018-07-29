# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('remote_app', '0002_auto_20180628_0525'),
    ]

    operations = [
        migrations.AlterField(
            model_name='remoteapp',
            name='auth_user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
    ]
