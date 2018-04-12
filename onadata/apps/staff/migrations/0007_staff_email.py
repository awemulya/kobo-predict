# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20180411_1233'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='email',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
