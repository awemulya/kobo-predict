# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0002_auto_20161108_0034'),
    ]

    operations = [
        migrations.AddField(
            model_name='site',
            name='logo',
            field=models.ImageField(default=b'media/logo/default_image.png', upload_to=b'media/logo'),
        ),
    ]
