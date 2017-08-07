# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fsforms', '0043_instanceimages'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='instancestatuschanged',
            options={'ordering': ['-date']},
        ),
    ]
