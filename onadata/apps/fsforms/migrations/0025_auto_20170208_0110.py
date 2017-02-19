# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0024_auto_20170202_0133'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='schedule',
            options={'ordering': ('-date_range_start', 'date_range_end'), 'verbose_name': 'Form Schedule', 'verbose_name_plural': 'Form Schedules'},
        ),
    ]
