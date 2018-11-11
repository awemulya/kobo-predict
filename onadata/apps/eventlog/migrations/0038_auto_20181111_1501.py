# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0037_auto_20180911_1252'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='celerytaskprogress',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='celerytaskprogress',
            name='object_id',
        ),
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_type',
            field=models.IntegerField(default=0, choices=[(0, 'Bulk Site Update'), (1, 'User Assign to Project'), (2, 'User Assign to Site'), (3, 'Site Response Xls Report'), (4, 'Site Import'), (6, 'Zip Site Images'), (7, 'Remove Roles'), (8, 'Site Data Export'), (9, 'Response Pdf Report'), (10, 'Site Progress Xls Report')]),
        ),
    ]
