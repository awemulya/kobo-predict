# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0053_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(null=True, base_field=models.IntegerField(), size=None),
        ),
    ]
