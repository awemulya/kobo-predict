# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0004_auto_20161212_0352'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(default=b'logo/default_image.png', upload_to=b'logo'),
        ),
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(default=b'media/logo/default_image.png', upload_to=b'logo'),
        ),
    ]
