# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0031_auto_20171121_1300'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timezone',
            old_name='city',
            new_name='time_zone',
        ),
    ]
