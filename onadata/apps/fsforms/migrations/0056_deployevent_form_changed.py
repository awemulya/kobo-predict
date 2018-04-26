# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0055_deployevent'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployevent',
            name='form_changed',
            field=models.BooleanField(default=True),
        ),
    ]
