# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0041_auto_20171128_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='cluster_sites_by_region',
        ),
        migrations.AddField(
            model_name='project',
            name='cluster_sites',
            field=models.BooleanField(default=False),
        ),
    ]
