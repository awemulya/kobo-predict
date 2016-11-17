# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0009_schedule_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='selected_days',
            field=models.ManyToManyField(related_name='days', to='fsforms.Days'),
        ),
    ]
