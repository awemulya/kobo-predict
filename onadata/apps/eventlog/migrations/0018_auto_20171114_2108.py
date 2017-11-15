# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0017_fieldsightlog_recipient'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightlog',
            name='seen_by',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
