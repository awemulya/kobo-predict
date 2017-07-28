# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0041_auto_20170718_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='project_stage_id',
            field=models.IntegerField(default=0),
        ),
    ]
