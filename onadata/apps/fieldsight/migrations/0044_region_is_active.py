# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0043_site_region'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
