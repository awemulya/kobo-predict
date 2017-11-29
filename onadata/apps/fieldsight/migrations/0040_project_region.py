# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0039_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='region',
            field=models.IntegerField(default=0, choices=[(0, 'No'), (1, 'Yes')]),
        ),
    ]
