# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0006_auto_20161117_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='days',
            name='day',
            field=models.CharField(max_length=9),
        ),
    ]
