# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0021_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fieldsightlog',
            name='extra_message',
            field=models.TextField(null=True, blank=True),
        ),
    ]
