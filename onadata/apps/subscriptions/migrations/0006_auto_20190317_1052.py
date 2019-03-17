# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0005_auto_20190315_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='invoice',
            name='deleted_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
