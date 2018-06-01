# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='geolayer',
            name='tolerance',
            field=models.FloatField(default=0.0001),
        ),
    ]
