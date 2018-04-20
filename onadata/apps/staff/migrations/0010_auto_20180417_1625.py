# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0009_auto_20180416_1438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='bank',
            field=models.ForeignKey(default=None, blank=True, to='staff.Bank', null=True),
        ),
    ]
