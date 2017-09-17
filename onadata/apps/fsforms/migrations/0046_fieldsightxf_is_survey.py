# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0045_auto_20170912_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='is_survey',
            field=models.BooleanField(default=False),
        ),
    ]
