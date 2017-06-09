# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0006_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fieldsightlog',
            options={'ordering': ['-date'], 'get_latest_by': '-date'},
        ),
        migrations.RemoveField(
            model_name='fieldsightlog',
            name='project',
        ),
    ]
