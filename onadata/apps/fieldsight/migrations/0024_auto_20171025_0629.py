# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0023_auto_20170829_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(upload_to=b'logo'),
        ),
    ]
