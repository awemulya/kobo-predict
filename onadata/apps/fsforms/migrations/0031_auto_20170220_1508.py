# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0030_fieldsightxf_is_deployed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightxf',
            name='is_deployed',
            field=models.BooleanField(default=False),
        ),
    ]
