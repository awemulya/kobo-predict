# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0044_auto_20190226_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='celerytaskprogress',
            name='task_type',
            field=models.IntegerField(default=0, choices=[(0, 'Bulk Site Update'), (1, 'User Assign to Project'), (2, 'User Assign to Site'), (3, 'Site Response Xls Report'), (4, 'Site Import'), (6, 'Zip Site Images'), (7, 'Remove Roles'), (8, 'Site Data Export'), (9, 'Response Pdf Report'), (10, 'Site Progress Xls Report'), (11, 'Project Statstics Report'), (12, 'Log Report'), (13, 'User Assign to Region'), (14, 'User Assign to an entire project'), (15, 'Auto Create Demo Project, Site, Forms')]),
        ),
    ]
