# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0004_export_fsxf'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='site',
            field=models.IntegerField(default=0),
        ),
    ]
