# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0050_auto_20180305_1213'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='schedule_level_id',
            new_name='schedule_level',
        ),
    ]
