# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import onadata.apps.fsforms.fieldsight_models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0009_auto_20170208_0110'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='identifier',
            field=onadata.apps.fsforms.fieldsight_models.IntegerRangeField(default=1, verbose_name=b'ID'),
            preserve_default=False,
        ),
    ]
