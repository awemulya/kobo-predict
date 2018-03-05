# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0049_schedule_schedule_level'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='schedule_level',
            new_name='schedule_level_id',
        ),
    ]
