# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0007_auto_20161117_0206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='date_range_end',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='date_range_start',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
