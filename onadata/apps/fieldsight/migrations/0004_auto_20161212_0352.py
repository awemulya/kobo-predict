# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0003_site_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='logo',
            field=models.ImageField(default=b'media/logo/default_image.png', upload_to=b'media/logo'),
        ),
        migrations.AddField(
            model_name='project',
            name='logo',
            field=models.ImageField(default=b'media/logo/default_image.png', upload_to=b'media/logo'),
        ),
    ]
