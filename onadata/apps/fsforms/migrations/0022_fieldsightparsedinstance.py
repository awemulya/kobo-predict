# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0003_auto_20160912_0311'),
        ('fsforms', '0021_auto_20170104_0435'),
    ]

    operations = [
        migrations.CreateModel(
            name='FieldSightParsedInstance',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('viewer.parsedinstance',),
        ),
    ]
