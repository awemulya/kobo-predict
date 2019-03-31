# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0008_package_period_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='plan',
            field=models.IntegerField(default=0, choices=[(0, b'Free'), (1, b'Basic Monthly Plan'), (2, b'Basic Yearly Plan'), (3, b'Extended Monthly Plan'), (4, b'Extended Yearly Plan'), (5, b'Pro Monthly Plan'), (6, b'Pro Yearly Plan'), (7, b'Scale Monthly Plan'), (8, b'Scale Yearly Plan'), (9, b'Starter Monthly Plan'), (10, b'Starter Yearly Plan')]),
        ),
    ]
