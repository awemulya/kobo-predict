# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0039_auto_20181111_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_type',
            field=models.IntegerField(default=0, choices=[(0, 'Bulk Site Update'), (1, 'User Assign to Project'), (2, 'User Assign to Site'), (3, 'Site Response Xls Report'), (4, 'Site Import'), (6, 'Zip Site Images'), (7, 'Remove Roles'), (8, 'Site Data Export'), (9, 'Response Pdf Report'), (10, 'Site Progress Xls Report'), (11, 'Project Statstics Report')]),
        ),
    ]
