# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0004_auto_20180409_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='date_of_birth',
            field=models.DateField(null=True, blank=True),
        ),
    ]
