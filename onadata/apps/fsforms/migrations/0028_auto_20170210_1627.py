# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0027_auto_20170210_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='name',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Schedule Name', blank=True),
        ),
    ]
