# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('eventlog', '0025_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightlog',
            name='extra_json',
            field=jsonfield.fields.JSONField(default=None, null=True, blank=True),
        ),
    ]
