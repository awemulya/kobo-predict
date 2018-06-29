# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0061_auto_20180610_1238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='identifier',
            field=models.CharField(max_length=255),
        ),
    ]
