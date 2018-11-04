# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0062_xformhistory_version'),
    ]

    operations = [
        migrations.AddField(
            model_name='finstance',
            name='version',
            field=models.CharField(default='', max_length=32),
        ),
    ]
