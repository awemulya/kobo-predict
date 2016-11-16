# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fsforms.models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0004_auto_20161115_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='order',
            field=onadata.apps.fsforms.models.IntegerRangeField(default=0),
        ),
    ]
