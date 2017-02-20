# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0029_fieldsightxf_fsform'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='is_deployed',
            field=models.BooleanField(default=True),
        ),
    ]
