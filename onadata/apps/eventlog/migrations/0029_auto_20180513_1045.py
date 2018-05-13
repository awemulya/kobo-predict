# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0028_auto_20180404_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
