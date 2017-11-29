# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0042_auto_20171128_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='region',
            field=models.ForeignKey(related_name='regions', blank=True, to='fieldsight.Region', null=True),
        ),
    ]
