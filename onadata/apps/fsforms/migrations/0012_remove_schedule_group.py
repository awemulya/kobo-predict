# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0011_fieldsightinstance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schedule',
            name='group',
        ),
    ]
