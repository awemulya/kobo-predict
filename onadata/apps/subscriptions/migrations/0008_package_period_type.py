# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_package_total_charge'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='period_type',
            field=models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Month'), (2, b'Year')]),
        ),
    ]
