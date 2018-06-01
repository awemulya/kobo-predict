# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0002_geolayer_tolerance'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='geolayer',
            options={'ordering': ['title', 'level']},
        ),
    ]
