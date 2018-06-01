# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0053_project_geo_layers'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='parent',
            field=models.ForeignKey(default=None, blank=True, to='fieldsight.Region', null=True),
        ),
    ]
