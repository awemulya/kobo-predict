# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0023_auto_20170130_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightxf',
            name='form_status',
            field=models.IntegerField(default=0, choices=[(0, b'Outstanding'), (1, b'Rejected'), (2, b'Flagged'), (3, b'Approved')]),
        ),
    ]
