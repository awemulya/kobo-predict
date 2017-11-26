# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0032_auto_20171121_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(default='logo/default_image.png', upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=models.ImageField(default='logo/default_image.png', upload_to='logo'),
        ),
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(default='logo/default_image.png', upload_to='logo'),
        ),
    ]
