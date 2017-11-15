# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0046_fieldsightxf_is_survey'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='from_project',
            field=models.BooleanField(default=True),
        ),
    ]
