# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0057_auto_20180426_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='finstance',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
