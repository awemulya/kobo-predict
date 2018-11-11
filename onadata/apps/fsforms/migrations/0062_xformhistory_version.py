# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0061_auto_20181009_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='xformhistory',
            name='version',
            field=models.CharField(default='', max_length=32),
        ),
    ]
