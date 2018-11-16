# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0063_finstance_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='finstance',
            name='version',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='xformhistory',
            name='version',
            field=models.CharField(default='', max_length=255),
        ),
    ]
