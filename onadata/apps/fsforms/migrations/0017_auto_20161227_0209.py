# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0016_stage_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stage',
            name='group',
            field=models.ForeignKey(related_name='stage', blank=True, to='fsforms.FormGroup', null=True),
        ),
    ]
