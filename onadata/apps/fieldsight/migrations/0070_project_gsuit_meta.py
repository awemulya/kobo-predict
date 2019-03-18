# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0069_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='gsuit_meta',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
