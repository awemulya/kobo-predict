# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_subscription_organization'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='extra_submissions_charge',
            field=models.FloatField(default=0),
        ),
    ]
