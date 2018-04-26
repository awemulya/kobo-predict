# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0056_deployevent_form_changed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(default=[], base_field=models.IntegerField(), size=None),
        ),
    ]
