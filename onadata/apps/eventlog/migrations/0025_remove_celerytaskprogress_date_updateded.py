# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0024_auto_20180316_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='celerytaskprogress',
            name='date_updateded',
        ),
    ]
