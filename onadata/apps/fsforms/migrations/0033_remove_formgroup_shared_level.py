# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0032_auto_20170221_1040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='formgroup',
            name='shared_level',
        ),
    ]
