# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0039_finstance_submitted_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldsightxf',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
