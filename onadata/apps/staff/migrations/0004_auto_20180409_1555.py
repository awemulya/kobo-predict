# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20180409_1513'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bank',
            old_name='bank_name',
            new_name='name',
        ),
    ]
