# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0060_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='parent',
            field=models.ForeignKey(related_name='children', default=None, blank=True, to='fieldsight.Region', null=True),
        ),
    ]
