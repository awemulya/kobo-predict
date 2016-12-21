# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0006_auto_20161214_0333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(default=b'logo/default_image.png', upload_to=b'logo'),
        ),
    ]
