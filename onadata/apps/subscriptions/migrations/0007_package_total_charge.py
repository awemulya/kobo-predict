# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_auto_20190317_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='total_charge',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
