# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0011_auto_20170210_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='identifier',
            field=models.CharField(max_length=255, verbose_name=b'ID'),
        ),
    ]
