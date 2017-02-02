# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fieldsight', '0007_auto_20161214_0334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(default=b'logo/default_org.png', upload_to=b'logo'),
        ),
        migrations.AlterField(
            model_name='project',
            name='logo',
            field=models.ImageField(default=b'logo/default_org.png', upload_to=b'logo'),
        ),
        migrations.AlterField(
            model_name='site',
            name='logo',
            field=models.ImageField(default=b'logo/default_site.png', upload_to=b'logo'),
        ),
    ]
